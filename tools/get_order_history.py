from typing import List
from schemas import OrderSchema
from tools.data_store import DataStore


class getOrderHistory:
    def __init__(self, data_store: DataStore):
        self.data_store = data_store

    def get_order_history(self, customer_id: str) -> List[OrderSchema]:
        """Fetches order history for a specific customer ID."""
        return [
            order
            for order in self.data_store.orders
            if order.customer_id.strip().upper() == customer_id.strip().upper()
        ]
