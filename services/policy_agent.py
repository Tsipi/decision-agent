import re
from datetime import datetime
from typing import Dict, Any, List
from tools.lookup_customer import lookupCustomer
from tools.get_order_history import getOrderHistory
from schemas import AgentDecision, OrderSchema

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
        actions = []

        # Extract customer ID from the request text
        customer_id_match = re.search(r"CUST_\d{3}", request_text)
        if not customer_id_match:
            return AgentDecision(
                decision="Error",
                reason="Customer ID not found in the request.",
                actions=[]
            )
        
        customer_id = customer_id_match.group(0)

        # Extract Order ID from the request text
        order_id_match = re.search(r"ORD_\d{3}", request_text)
        if not order_id_match:
            return AgentDecision(
                decision="ESCALATE",
                reason="Order ID not found in the request.",
                actions=[]
            )

        order_id = order_id_match.group(0)


        # Extract amount from the request text (must be written with a $, decimals optional)
        amount_match = re.search(r"\$(\d+(?:\.\d+)?)", request_text)
        if not amount_match:
            return AgentDecision(
                decision="ESCALATE",
                reason="Amount not found in the request.",
                actions=[]
            )

        amount = float(amount_match.group(1))
        decision = "ESCALATE"
        reason = "Default reason."
        
        # Step 4: return the structured decision + reasoning trace.
        return AgentDecision(decision=decision, reason=reason, actions=[])
