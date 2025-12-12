from dataclasses import dataclass
from typing import Optional
from datetime import datetime

@dataclass
class MenuItem:
    id: Optional[int]
    name: str
    price: float

@dataclass
class Table:
    id: Optional[int]
    table_number: int
    status: str  # available / occupied

@dataclass
class OrderItem:
    id: Optional[int]
    order_id: Optional[int]
    item_id: int
    quantity: int

@dataclass
class Order:
    id: Optional[int]
    table_id: int
    order_time: Optional[datetime]
    status: str  # received/preparing/ready/paid
