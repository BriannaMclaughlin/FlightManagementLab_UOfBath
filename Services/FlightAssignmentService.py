from datetime import datetime
from typing import Optional

from FlightManagementLab_UOfBath.Entities.Flight import Flight
from FlightManagementLab_UOfBath.Repositories.FlightAssignmentRepository import FlightAssignmentRepository

class FlightAssignmentService():
    def __init__(self, db_path="FlightManagementDB.db"):
        self.flight_assignment_repo = FlightAssignmentRepository(db_path)

    def get_flights_for_pilot(self, pilot_id: int) -> list[int]:
        return self.flight_assignment_repo.get_flights_for_pilot(pilot_id=pilot_id)

    def get_pilots_for_flight(self, flight_id: int) -> list[int]:
        return self.flight_assignment_repo.get_pilots_for_flight(flight_id=flight_id)

    def assign_pilot_to_flight(self, flight_id, pilot_id) -> bool:
        return self.flight_assignment_repo.assign_pilot_to_flight(flight_id=flight_id, pilot_id=pilot_id)

    def unassign_pilot_from_flight(self, flight_id, pilot_id) -> bool:
        return self.flight_assignment_repo.unassign_pilot_from_flight(flight_id=flight_id, pilot_id=pilot_id)

    def unassign_all_pilots_from_flight(self, flight_id) -> bool:
        return self.flight_assignment_repo.unassign_all_pilots_from_flight(flight_id=flight_id)
