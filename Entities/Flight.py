from dataclasses import dataclass
import datetime
from typing import Optional


@dataclass
class Flight:
    status: str
    scheduledDepart: datetime
    scheduledArrive: datetime
    originAirport: str  # Foreign Key
    destinationAirport: str  # Foreign Key
    actualDepart: Optional[datetime] = None # Default is none for before flight happens
    actualArrive: Optional[datetime] = None
    id: Optional[int] = None # Primary Key -> DB will assign
    # could add plane id if I want to create a plane entity.