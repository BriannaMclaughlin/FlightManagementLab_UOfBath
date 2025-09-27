from dataclasses import dataclass
import datetime

@dataclass
class FlightAssignment:
    flightId: int
    pilotId: int