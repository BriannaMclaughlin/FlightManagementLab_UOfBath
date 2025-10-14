from dataclasses import dataclass
import datetime
from typing import Optional


@dataclass
class Flight:
    status: str
    scheduled_depart: datetime
    scheduled_arrive: datetime
    origin_airport: str  # Foreign Key
    destination_airport: str  # Foreign Key
    actual_depart: Optional[datetime] = None # Default is none for before flight happens
    actual_arrive: Optional[datetime] = None
    id: Optional[int] = None # Primary Key -> DB will assign
    # could add plane id if I want to create a plane entity.