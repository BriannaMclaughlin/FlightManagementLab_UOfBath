from dataclasses import dataclass

@dataclass
class FlightDetails:
    id: int
    status: str
    scheduledDepart: str
    scheduledArrive: str
    actualDepart: str | None
    actualArrive: str | None
    origin: dict         # {airportId, airportName, city, country, continent}
    destination: dict    # {airportId, airportName, city, country, continent}
    pilots: list[dict]   # list of {pilotId, firstName, lastName, rank}