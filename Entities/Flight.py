from dataclasses import dataclass
import datetime

@dataclass
class Flight:
    id: int
    flightNumber: str
    status: str
    scheduledDepart: datetime
    scheduledArrive: datetime
    actualDepart: datetime
    actualArrive: datetime