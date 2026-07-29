## MVP task - Customer-Service Refund Policy Agent

A tool-using agent that turns **free-text customer requests** into **structured, auditable decisions** — `APPROVED`, `REJECT`, or `ESCALATE` — each with a plain-language reasoning trace.

The agent parses a natural-language request, looks up the relevant customer and order through dedicated tools, applies a set of business rules, and returns a validated [Pydantic](https://docs.pydantic.dev/) object. Every decision is explainable and every output is schema-checked.

Scenario: A customer submits a free-text request (e.g., a refund request, an account question, or a
complaint). 

### Decision pipeline

1. **Parse** the request and extract relevant details (customer ID, request type, amount, etc.)

2. **Look up** relevant information using the provided tools (e.g., customer record, order history)

3. **Decide** on an action: APPROVE , REJECT , or ESCALATE — based on clear business rules

4. **Return a structured decision with a reasoning** trace explaining why

The pipeline is built from **guard clauses** that fail fast: each missing or invalid piece returns early with a decision, so by the time the rule engine runs, all required data is guaranteed present.

## Provided Resources
customers.json — customer records (id, name, email, tier, status)
orders.json — orders linked to customers (amount, date, status)
sample_requests.json — free-text requests to run your agent against

## Business Rules
If user asks - the decision will be as following
1. Refund under $50 AND order placed within 30 days - APPROVED
2. Refund over $500 OR order older than 90 days - ESCALATE
3. No matching customer or order found - REJECT
4. Ambiguous / incomplete request (missing key info) - EXCALATE

e.g.Some cases intentionally fall in a gray area (e.g., a $75 refund within 30 days). We want to see how your agent
reasons about them. Feel free to extend the rules — just document your choices.

Evaluated **in this order** — the safer (ESCALATE/REJECT) conditions are checked before auto-approval, so a risky refund can never slip through.

## Requirements
1. Tha agent should use 2 tools lookup_customner, get_order_history
2. The output should be structures (Pydantic model / JSON schema) with decision and reasoning
3. hadle edge cases (missing data, ambiguous input, invalid request)
4. in the README should add (Design, key tradeoffs and improvement suggestiuons)
5. write also in the README some example inputs to ran with the outputs

## Nice to have 
1. Basic evaluation: a small set of test cases with 
expected outcomes and a script that checks them
2. Basic observability/tracing (LangSmith, Langfuse, or even structured logging)
3. Notes on how you'd measure quality in production


## Architecture

```
main.py                  # Entry point: loads requests, runs the agent, prints colored output
schemas.py               # Pydantic models: CustomerSchema, OrderSchema, AgentDecision
services/
  policy_agent.py        # PolicyAgent — parsing, lookups, and the business-rule engine
tools/
  data_store.py          # Shared data layer: loads the JSON files once
  lookup_customer.py     # Tool 1: resolve a customer record by ID
  get_order_history.py   # Tool 2: fetch a customer's orders
data/
  customers.json         # Customer records (id, name, email, tier, status)
  orders.json            # Orders (id, customer_id, amount, date, status)
  sample_requests.json   # Free-text requests to run the agent against
```
---

## Setup & run

Requires **Python 3.10+** and `pydantic`.

```bash
pip install pydantic
python main.py
```

Output is color-coded in the terminal: green `APPROVED`, yellow `ESCALATE`, red `REJECT`.


---

## Example runs

Run against `data/sample_requests.json` (decision date fixed at **2026-06-01** for reproducibility):

| Request | Input (abridged) | Decision | Why |
|---------|------------------|----------|-----|
| R1 | refund `ORD_101` "45$" — CUST_001 | `ESCALATE` | amount not written as `$45` → unparseable |
| R2 | refund `ORD_103` ($600) — CUST_002 | `ESCALATE` | over the $500 limit |
| R3 | refund `ORD_102` $75 — CUST_001 | `ESCALATE` | gray area ($50–$500) |
| R4 | refund `ORD_104` — CUST_003 | `ESCALATE` | no amount given |
| R5 | refund, "won't tell you the price" — CUST_001 | `ESCALATE` | no order ID or amount |
| R6 | fraud on CUST_999, `ORD_888` | `ESCALATE` | no amount given |
| R7 | refund $50 `ORD_888` — CUST_999 | `REJECT` | customer does not exist |
| R8 | refund $50 `ORD_777` — CUST_001 | `REJECT` | order does not exist |
| R9 | refund $30 `ORD_101` — CUST_001 | `APPROVED` | under $50 and 12 days old |

### Sample output

**APPROVED**
```json
{
  "decision": "APPROVED",
  "reason": "Refund $30.00 on order ORD_101 is under $50 and was placed 12 days ago (within 30 days).",
  "actions": []
}
```
---

## Design decisions & tradeoffs

**Deterministic date instead of `datetime.now()`.**
`PolicyAgent` takes a `current_date` (default `2026-06-01`). This keeps the age-based rules reproducible — tests won't silently break as real time passes.

**Amount must be written with a `$`.**
Amounts are parsed with `\$(\d+(?:\.\d+)?)`. Anchoring on `$` avoids false positives — the request text is full of digits (`CUST_001`, `ORD_101`) 

**Refund amount comes from the request, not the order total.**
The agent decides on the amount the *customer asks to refund*, supporting partial refunds. It does **not** yet validate that the refund is ≤ the order total — a natural next guardrail (see below).

**ESCALATE as the default for uncertainty.**
Incomplete requests and gray-area amounts escalate rather than being auto-approved or auto-rejected.

**Single shared data layer.**
A `DataStore` loads `customers.json` and `orders.json` once, and both tools read from it via dependency injection. This avoids duplicated file I/O and gives the tools one consistent source of truth. Swapping the JSON files for a real database later means changing only `DataStore`, not the tools.