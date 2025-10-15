from datetime import datetime
from typing import Optional

from FlightManagementLab_UOfBath.Entities.Flight import Flight
from FlightManagementLab_UOfBath.Repositories.FlightRepository import FlightRepository


class FlightService:
    def __init__(self, db_path="FlightManagementDB.db"):
        self.flight_repo = FlightRepository(db_path)

    def get_flight(self, flight_id: int):
        try:
            return self.flight_repo.get(flight_id=flight_id)
        except ValueError as e:
            print(e)
            print("\n")
            return None

    def get_flight_details(self, flight_id):
        try:
            return self.flight_repo.get_flight_details(flight_id=flight_id)
        except ValueError as e:
            print(e)
            print("\n")
            return None

    def add_flight(self,
                  status: str,
                  origin_airport: str,
                  destination_airport: str,
                  scheduled_depart: Optional[datetime] = None,
                  scheduled_arrive: Optional[datetime] = None,
                  actual_depart: Optional[datetime] = None,
                  actual_arrive: Optional[datetime] = None) -> None:

        flight = Flight(
            status=status,
            scheduled_depart=scheduled_depart,
            scheduled_arrive=scheduled_arrive,
            actual_depart=actual_depart,
            actual_arrive=actual_arrive,
            origin_airport=origin_airport,
            destination_airport=destination_airport
        )

        self.flight_repo.add(flight=flight)

    def delete_flight(self, flight_id):
        self.flight_repo.delete(flight_id)

    def update_flight(self, flight_id: int, **kwargs: object) -> bool:
        return self.flight_repo.update(flight_id, **kwargs)

    def find_by_origin(self, origin: str, start: datetime, end: datetime) -> str:
        result = self.flight_repo.find_by_origin(origin, start, end)
        string = ""
        if result:
            for flight in result:
                string += (f"ID -> {flight.id}: {flight.origin_airport} to {flight.destination_airport} "
                           f"({flight.status}) on {flight.scheduled_depart} \n")

        if len(string) > 0:
            return string
        else:
            string += f"No flights available during that time frame with an origin of {origin}"
            return string

    def find_by_destination(self, destination: str, start: datetime, end: datetime) -> str:
        result = self.flight_repo.find_by_destination(destination, start, end)
        string = ""
        if result:
            for flight in result:
                string += (f"ID -> {flight.id}: {flight.origin_airport} to {flight.destination_airport} "
                           f"({flight.status}) on {flight.scheduled_depart} \n")

        if len(string) > 0:
            return string
        else:
            string += f"No flights available during that time frame with a destination of {destination}"
            return string

    def find_by_origin_and_destination(self, origin: str, destination: str, start: datetime, end: datetime) -> str:
        result = self.flight_repo.find_by_origin_and_destination(origin, destination, start, end)
        string = ""
        if result:
            for flight in result:
                string += (f"ID -> {flight.id}: {flight.origin_airport} to {flight.destination_airport} "
                           f"({flight.status}) on {flight.scheduled_depart} \n")

        if len(string) > 0:
            return string
        else:
            string += (f"No flights available during that time frame with an origin of {origin} and a destination "
                       f"of {destination}")
            return string

    def flight_exists(self, flight_id: int):
        try:
            flight = self.flight_repo.get(flight_id)
            if flight:
                return True
        except ValueError:
            return False