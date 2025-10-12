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

    def find_by_last_name(self, last_name: str) -> str:
        result =  self.pilot_repo.find_by_last_name(last_name)
        string = ""
        if result:
            for pilot in result:
                active = ""
                if pilot.active:
                    active = "Active"
                else:
                    active = "Inactive"
                string += (f"ID -> {pilot.id}: {pilot.rank} {pilot.first_name} {pilot.last_name} ({active}), "
                           f"Home Airport: {pilot.home_airport} \n")

        if len(string) > 0:
            return string
        else:
            string += f"No pilots available with a last name of {last_name}"

    def pilotExists(self, pilot_id: int):
        try:
            pilot = self.pilot_repo.get(pilot_id)
            if pilot:
                return True
        except ValueError as e:
            return False