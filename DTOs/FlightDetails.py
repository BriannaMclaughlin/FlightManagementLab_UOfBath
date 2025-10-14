from dataclasses import dataclass

@dataclass
class FlightDetails:
    id: int
    status: str
    scheduled_depart: str
    scheduled_arrive: str
    actual_depart: str | None
    actual_arrive: str | None
    origin: dict         # {airportId, airportName, city, country, continent}
    destination: dict    # {airportId, airportName, city, country, continent}
    pilots: list[dict]   # list of {pilotId, firstName, lastName, rank}