from dataclasses import dataclass

@dataclass
class Destination:
    airport_id: str
    airport_name: str
    country: str
    city: str

