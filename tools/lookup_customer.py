from typing import Optional
from schemas import CustomerSchema
from tools.data_store import DataStore


class lookupCustomer:
    def __init__(self, data_store: DataStore):
        self.data_store = data_store

    def lookup_customer(self, customer_id: str) -> Optional[CustomerSchema]:
        """Fetches profile records for a specific customer ID."""
        for cust in self.data_store.customers:
            if cust.id.strip().upper() == customer_id.strip().upper():
                return cust
        return None
