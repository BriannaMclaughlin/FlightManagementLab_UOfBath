from FlightManagementLab_UOfBath.Entities.Destination import Destination
from FlightManagementLab_UOfBath.Repositories.DestinationRepository import DestinationRepository


class DestinationService():
    def __init__(self, db_path="FlightManagementDB.db"):
        self.destinationRepo = DestinationRepository(db_path)

    def getDestination(self, airportId: str):
        try:
            return self.destinationRepo.get(airportId=airportId)
        except ValueError as e:
            print(e)
            print("\n")
            return None

    def destinationExists(self, airportId: str):
        try:
            destination = self.destinationRepo.get(airportId=airportId)
            if destination:
                return True
        except ValueError as e:
            return False

    def find_by_city(self, city: str) -> str:
        result =  self.destinationRepo.find_by_city(city)
        string = ""
        if result:
            for destination in result:
                string += (f"{destination.airportId}: {destination.airportName}, {destination.city}, "
                           f"{destination.country} \n")

        if len(string) > 0:
            return string
        else:
            string += f"No destinations available with for {city}"

    def find_by_country(self, country: str) -> list[Destination]:
        return self.destinationRepo.find_by_country(country)

    def add(self, destination: Destination | None = None, **kwargs: object) -> None:
        if destination:
            self.destinationRepo.add()
        else:
            self.destinationRepo.add(**kwargs)
