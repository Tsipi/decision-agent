import re
from datetime import datetime
from tools.lookup_customer import lookupCustomer
from tools.get_order_history import getOrderHistory
from schemas import AgentDecision

class PolicyAgent:
    def __init__(self, customer_lookup: lookupCustomer, order_history: getOrderHistory, current_date: str = "2026-06-01"):
        self.customer_lookup = customer_lookup
        self.order_history = order_history

        self.current_date = datetime.strptime(current_date, "%Y-%m-%d")

    def _calculate_days_ago(self, order_date_str: str) -> int:
        order_date = datetime.strptime(order_date_str, "%Y-%m-%d")
        return (self.current_date - order_date).days

    def process_request(self, request_text: str) -> AgentDecision:
        """Processes a customer service request and returns a decision."""

        # Extract customer ID from the request text
        customer_id_match = re.search(r"CUST_\d{3}", request_text)
        if not customer_id_match:
            return AgentDecision(
                decision="Error",
                reason="Customer ID not found in the request.",
            )
        
        customer_id = customer_id_match.group(0)

        # Extract Order ID from the request text
        order_id_match = re.search(r"ORD_\d{3}", request_text)
        if not order_id_match:
            return AgentDecision(
                decision="ESCALATE",
                reason="Order ID not found in the request."
            )

        order_id = order_id_match.group(0)


        # Extract amount from the request text (must be written with a $, decimals optional)
        amount_match = re.search(r"\$(\d+(?:\.\d+)?)", request_text)
        if not amount_match:
            return AgentDecision(
                decision="ESCALATE",
                reason="Amount not found in the request."
            )

        amount = float(amount_match.group(1))

        # Lookup customer profile
        customer_profile = self.customer_lookup.lookup_customer(customer_id)
        if not customer_profile:
            return AgentDecision(
                decision="REJECT",
                reason=f"No profile found for Customer ID {customer_id}."
            )
        
        # Step 1: find the specific order this request is about.
        # get_order_history returns ALL of the customer's orders, so I
        # loop through them to find the one whose id matches order_id.
        orders = self.order_history.get_order_history(customer_profile.id)
        target_order = None
        for order in orders:
            if order.id.strip().upper() == order_id.strip().upper():
                target_order = order
                break

        # Rule 3: no matching order found -> REJECT
        if target_order is None:
            return AgentDecision(
                decision="REJECT",
                reason=f"No order {order_id} found for customer {customer_id}."
            )

        # Step 2: how many days ago was this order placed?
        # target_order.date is a string like "2026-07-10"; the helper
        # turns it into a date and subtracts it from self.current_date.
        days_ago = self._calculate_days_ago(target_order.date)

        # Step 3: apply the business rules from the README.
        # Order matters: we check the ESCALATE conditions BEFORE the
        # APPROVED one, so a risky refund never slips through.
        if amount > 500 or days_ago > 90:
            # Rule 2: high-value OR stale order -> needs a human.
            decision = "ESCALATE"
            reason = (
                f"Refund ${amount:.2f} on order {order_id} placed {days_ago} "
                f"days ago exceeds the $500 limit or the 90-day window."
            )
        elif amount < 50 and days_ago <= 30:
            # Rule 1: small AND recent -> safe to auto-approve.
            decision = "APPROVED"
            reason = (
                f"Refund ${amount:.2f} on order {order_id} is under $50 and "
                f"was placed {days_ago} days ago (within 30 days)."
            )
        else:
            # Gray area (e.g. a $75 refund within 30 days): the README
            # rules don't cover it, so we default to ESCALATE for review.
            decision = "ESCALATE"
            reason = (
                f"Refund ${amount:.2f} on order {order_id} placed {days_ago} "
                f"days ago falls outside the auto-approve rules; escalating."
            )

        # Step 4: return the structured decision + reasoning trace.
        return AgentDecision(decision=decision, reason=reason)
