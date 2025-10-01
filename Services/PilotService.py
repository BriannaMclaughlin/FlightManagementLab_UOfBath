from FlightManagementLab_UOfBath.Entities.Pilot import Pilot
from FlightManagementLab_UOfBath.Repositories.PilotRepository import PilotRepository


class PilotService:
    def __init__(self, db_path="FlightManagementDB.db"):
        self.pilot_repo = PilotRepository(db_path)

    def get_pilot(self, pilot_id: int):
        try:
            return self.pilot_repo.get(id=pilot_id)
        except ValueError as e:
            print(e)
            print("\n")
            return None

    def add_pilot(self,
                 first_name: str,
                 last_name: str,
                 license_number: str,
                 rank: str,
                 experience_hours: int,
                 home_airport: str) -> None:

        pilot = Pilot(
            first_name=first_name,
            last_name=last_name,
            license_number=license_number,
            rank=rank,
            experience_hours=experience_hours,
            home_airport=home_airport
        )

        self.pilot_repo.add(pilot=pilot)

    def delete_pilot(self, pilot_id):
        self.pilot_repo.delete(pilot_id)

    def update_pilot(self, pilot_id, **kwargs):
        self.pilot_repo.update(pilot_id=pilot_id, **kwargs)