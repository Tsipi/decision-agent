import json
from typing import List
from schemas import CustomerSchema, OrderSchema


class DataStore:
    """Loads customer and order data from disk once and shares it across tools.

    Both tools read from the same in-memory lists, so each JSON file is
    parsed a single time instead of once per tool.
    """

    def __init__(
        self,
        customers_path: str = "data/customers.json",
        orders_path: str = "data/orders.json",
    ):
        with open(customers_path, "r") as f:
            self.customers: List[CustomerSchema] = [
                CustomerSchema(**cust) for cust in json.load(f)
            ]

        with open(orders_path, "r") as f:
            self.orders: List[OrderSchema] = [
                OrderSchema(**order) for order in json.load(f)
            ]
