# decision-agent

Build and MVP agent that receives a free-text customer request and resolves it by reasoning over
available tools and data.

Scenario: A customer submits a free-text request (e.g., a refund request, an account question, or a
complaint). 

The agent should:
1. Parse the request and extract relevant details (customer ID, request type, amount, etc.)

2. Look up relevant information using the provided tools (e.g., customer record, order history)

3. Decide on an action: APPROVE , REJECT , or ESCALATE — based on clear business rules

4. Return a structured decision with a reasoning trace explaining why

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
