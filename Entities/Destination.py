from dataclasses import dataclass

@dataclass
class Destination:
    airportId: str
    airportName: str
    continent: str
    country: str
    city: str

