from dataclasses import dataclass
import datetime
from typing import Optional


@dataclass
class Pilot:
    first_name: str
    last_name: str
    license_number: str
    rank: str
    experience_hours: int
    home_airport: str # Foreign Key
    active: Optional[bool] = True #defaults to active when created
    id: Optional[int] = None  # Primary Key -> DB will assign
    