from datetime import datetime
from operator import truediv

from FlightManagementLab_UOfBath.Entities.Flight import Flight
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

    def delete_pilot(self, pilot_id) -> bool:
        return self.pilot_repo.delete(pilot_id)

    def update_pilot(self, pilot_id, **kwargs) -> bool:
        return self.pilot_repo.update(pilot_id=pilot_id, **kwargs)

    def find_by_last_name(self, last_name: str) -> str:
        result =  self.pilot_repo.find_by_last_name(last_name)
        string = ""
        if result:
            for pilot in result:
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
            return string

    def pilot_exists(self, pilot_id: int):
        try:
            pilot = self.pilot_repo.get(pilot_id)
            if pilot:
                return True
        except ValueError:
            return False

    def add_flight_hours(self, pilot_id: int, hours: int) -> bool:
        return self.pilot_repo.add_flight_hours(pilot_id=pilot_id, hours=hours)

    def daily_hours_allowed(self, pilot_id: int, date: datetime, expected_hours: int) -> bool:
        current_hours = self.pilot_repo.get_daily_flight_hours_for_pilot(pilot_id, date)
        requested_hours = int(current_hours) + expected_hours
        if requested_hours <= 8.0:
            return True
        else:
            return False

    def check_hours(self, pilot_id: int, flight: Flight) -> bool:
        depart_day = flight.scheduled_depart.date()
        arrive_day = flight.scheduled_arrive.date()

        if depart_day == arrive_day:
            expected_hours = int((flight.scheduled_arrive - flight.scheduled_depart).total_seconds() / 3600)
            allowed = self.daily_hours_allowed(pilot_id, depart_day, expected_hours)
            if allowed is False:
                print(f"Pilot {pilot_id} cannot be assigned to {flight.id}. ❌ \n"
                      f"Pilots are allowed to be scheduled for 8 hours a day, "
                      f"{expected_hours} hours will put Pilot {pilot_id} above this limit.")
            return allowed
        else:
            day_1_expected_hours = int((datetime.combine(flight.scheduled_depart.date(), datetime.max.time())
                                    - flight.scheduled_depart).total_seconds() / 3600)
            day_2_expected_hours = int((flight.scheduled_arrive
                                    - datetime.combine(flight.scheduled_arrive.date(), datetime.min.time())).total_seconds() / 3600)
            day_1_allowed = self.daily_hours_allowed(pilot_id, depart_day, day_1_expected_hours)
            day_2_allowed = self.daily_hours_allowed(pilot_id, arrive_day, day_2_expected_hours)

            if day_1_allowed is False:
                print(f"Pilot {pilot_id} cannot be assigned to {flight.id}. ❌ \n"
                      f"Pilots are allowed to be scheduled for 8 hours a day, "
                      f"{day_1_expected_hours} hours will put Pilot {pilot_id} above this limit on {depart_day}.")

            if day_2_allowed is False:
                print(f"Pilot {pilot_id} cannot be assigned to {flight.id}. ❌ \n"
                      f"Pilots are allowed to be scheduled for 8 hours a day. "
                      f"{day_2_expected_hours} hours will put Pilot {pilot_id} above this limit on {arrive_day}.")

            return day_1_allowed and day_2_allowed



