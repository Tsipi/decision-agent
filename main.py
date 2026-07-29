import os
import json
from tools.data_store import DataStore
from tools.lookup_customer import lookupCustomer
from tools.get_order_history import getOrderHistory
from services import PolicyAgent

# On Windows, older consoles ignore ANSI color codes unless we turn on
# "virtual terminal processing". This asks Windows to enable it.
if os.name == "nt":
    import ctypes
    _kernel32 = ctypes.windll.kernel32
    # -11 = stdout handle; 7 = enable processed output + ANSI (VT) processing.
    _kernel32.SetConsoleMode(_kernel32.GetStdHandle(-11), 7)

# ANSI escape codes: wrap text in a color, then RESET back to normal.
RESET = "\033[0m"
DECISION_COLORS = {
    "APPROVED": "\033[32m",  # green
    "ESCALATE": "\033[33m",  # yellow
    "REJECT": "\033[31m",    # red
}

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
        # Pick a color based on the decision (default: no color).
        color = DECISION_COLORS.get(decision.decision, "")
        print(f"{color}{decision.model_dump_json(indent=2)}{RESET}")
        print("-" * 60)

if __name__ == "__main__":
    main()
