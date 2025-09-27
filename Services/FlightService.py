from datetime import datetime
from typing import Optional

from FlightManagementLab_UOfBath.Entities.Flight import Flight
from FlightManagementLab_UOfBath.Repositories.FlightRepository import FlightRepository


class FlightService():
    def __init__(self, db_path="FlightManagementDB.db"):
        self.flightRepo = FlightRepository(db_path)

    def getFlight(self, id: int):
        try:
            return self.flightRepo.get(id=id)
        except ValueError as e:
            print(e)
            print("\n")
            return None

    def addFlight(self,
                  status: str,
                  originAirport: str,
                  destinationAirport: str,
                  scheduledDepart: Optional[datetime] = None,
                  scheduledArrive: Optional[datetime] = None,
                  actualDepart: Optional[datetime] = None,
                  actualArrive: Optional[datetime] = None) -> None:

        flight = Flight(
            status=status,
            scheduledDepart=scheduledDepart,
            scheduledArrive=scheduledArrive,
            actualDepart=actualDepart,
            actualArrive=actualArrive,
            originAirport=originAirport,
            destinationAirport=destinationAirport
        )

        self.flightRepo.add(flight=flight)

    def deleteFlight(self, id):
        self.flightRepo.delete(id)