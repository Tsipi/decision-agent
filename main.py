import os
import json
from tools.data_store import DataStore
from tools.lookup_customer import lookupCustomer
from tools.get_order_history import getOrderHistory
from services import PolicyAgent

def main():
    # Load the data once and share it across both tools.
    data_store = DataStore()
    customer_lookup = lookupCustomer(data_store)
    order_history = getOrderHistory(data_store)
    agent = PolicyAgent(customer_lookup=customer_lookup, order_history=order_history)

    with open("data/sample_requests.json", "r") as f:
        requests = json.load(f)
        
    print(f"============================================================")
    print(f"RUNNING CUSTOMER SERVICE POLICY AGENT SIMULATION (2026-06-16)")
    print(f"============================================================\n")
    
    for req in requests:
        print(f"Input Request [{req['id']}]: \"{req['text']}\"")
        decision = agent.process_request(req['text'])
        print(f"{decision.model_dump_json(indent=2)}")
        print("-" * 60)

if __name__ == "__main__":
    main()
