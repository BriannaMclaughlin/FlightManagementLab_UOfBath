from dataclasses import dataclass

@dataclass
class Destination:
    airportId: str
    airportName: str
    country: str
    city: str

