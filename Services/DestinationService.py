from FlightManagementLab_UOfBath.Entities.Destination import Destination
from FlightManagementLab_UOfBath.Repositories.DestinationRepository import DestinationRepository


class DestinationService:
    def __init__(self, db_path="FlightManagementDB.db"):
        self.destination_repo = DestinationRepository(db_path)

    def get_destination(self, airport_id: str):
        try:
            return self.destination_repo.get(airport_id=airport_id)
        except ValueError as e:
            print(e)
            print("\n")
            return None

    def destination_exists(self, airport_id: str):
        try:
            destination = self.destination_repo.get(airport_id=airport_id)
            if destination:
                return True
        except ValueError:
            return False

    def find_by_city(self, city: str) -> str:
        result =  self.destination_repo.find_by_city(city)
        string = ""
        if result:
            for destination in result:
                string += (f"{destination.airport_id}: {destination.airport_name}, {destination.city}, "
                           f"{destination.country} \n")

        if len(string) > 0:
            return string
        else:
            string += f"No destinations available with for {city}"
            return string

    def find_by_country(self, country: str) -> list[Destination]:
        return self.destination_repo.find_by_country(country)

    def add(self, destination: Destination | None = None, **kwargs: object) -> None:
        if destination:
            self.destination_repo.add()
        else:
            self.destination_repo.add(**kwargs)

    def update(self, airport_id: str, **kwargs) -> bool:
        return self.destination_repo.update(airport_id=airport_id, **kwargs)

    def delete(self, airport_id: str) -> bool:
        return self.destination_repo.delete(airport_id)