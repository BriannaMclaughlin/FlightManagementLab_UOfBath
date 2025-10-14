from dataclasses import dataclass
import datetime

@dataclass
class FlightAssignment:
    flight_id: int
    pilot_id: int