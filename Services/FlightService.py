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

    def get_flight_details(self, flight_id):
        try:
            return self.flightRepo.get_flight_details(flight_id=flight_id)
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

    def update_flight(self, id: int, **kwargs: object) -> None:
        self.flightRepo.update(id, **kwargs)

    def find_by_origin(self, origin: str, start: datetime, end: datetime) -> str:
        result = self.flightRepo.find_by_origin(origin, start, end)
        string = ""
        if result:
            for flight in result:
                string += (f"ID -> {flight.id}: {flight.originAirport} to {flight.destinationAirport} "
                           f"({flight.status}) on {flight.scheduledDepart} \n")

        if len(string) > 0:
            return string
        else:
            string += f"No flights available during that time frame with an origin of {origin}"
            return string

    def find_by_destination(self, destination: str, start: datetime, end: datetime) -> str:
        result = self.flightRepo.find_by_destination(destination, start, end)
        string = ""
        if result:
            for flight in result:
                string += (f"ID -> {flight.id}: {flight.originAirport} to {flight.destinationAirport} "
                           f"({flight.status}) on {flight.scheduledDepart} \n")

        if len(string) > 0:
            return string
        else:
            string += f"No flights available during that time frame with a destination of {destination}"
            return string

    def find_by_origin_and_destination(self, origin: str, destination: str, start: datetime, end: datetime) -> str:
        result = self.flightRepo.find_by_origin_and_destination(origin, destination, start, end)
        string = ""
        if result:
            for flight in result:
                string += (f"ID -> {flight.id}: {flight.originAirport} to {flight.destinationAirport} "
                           f"({flight.status}) on {flight.scheduledDepart} \n")

        if len(string) > 0:
            return string
        else:
            string += (f"No flights available during that time frame with an origin of {origin} and a destination "
                       f"of {destination}")
            return string