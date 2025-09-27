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