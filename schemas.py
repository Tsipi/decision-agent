from pydantic import BaseModel
from typing import List, Literal

class CustomerSchema(BaseModel):
    id: str
    name: str
    email: str
    tier: str
    status: str

class OrderSchema(BaseModel):
    id: str
    customer_id: str
    amount: float
    date: str
    status: str

class AgentDecision(BaseModel):
    decision: Literal["APPROVED", "REJECT", "ESCALATE"]
    reason: str
    actions: List[str]