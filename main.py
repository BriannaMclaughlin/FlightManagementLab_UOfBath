from datetime import datetime

from FlightManagementLab_UOfBath.Entities.Destination import Destination
from FlightManagementLab_UOfBath.Repositories.DestinationRepository import DestinationRepository
import sqlite3

from FlightManagementLab_UOfBath.Services.DestinationService import DestinationService
from FlightManagementLab_UOfBath.Services.FlightService import FlightService

destinationService = DestinationService()
flightService = FlightService()

def startRepositories():
    global destinationRepo
    destinationRepo = DestinationRepository("FlightManagementDB.db")

def ask_for_datetime(label: str) -> datetime | None:
    while True:
        year = input(f"Enter {label} year: ")
        if not year.isnumeric():
            print("Invalid year")
            continue
        year = int(year)

        month = input(f"Enter {label} month: ")
        if not month.isnumeric():
            print("Invalid month")
            continue
        month = int(month)

        day = input(f"Enter {label} day: ")
        if not day.isnumeric() or int(day) > 31:
            print("Invalid day")
            continue
        day = int(day)

        timeRaw = input(f"Enter {label} time (HH:MM): ")
        try:
            hour, minute = map(int, timeRaw.split(":"))
            if not (0 <= hour <= 23 and 0 <= minute <= 59):
                raise ValueError
        except Exception:
            print("Invalid time")
            continue

        return datetime(year, month, day, hour, minute)

def flightMenu(service: FlightService):
    print("Flight Information \n")
    while True:
        userinputraw = input("Would you like to: \n"
                          "1. View a flights information \n"
                          "2. Update a flights information \n"
                          "3. Add a flight \n"
                          "4. Delete a flight \n"
                          "* input 'back' to return to main menu * \n")

        userinput = userinputraw.strip().lower()

        if userinput == "back":
            return

        if userinput == "1":
            while True:
                userinputraw = input("Please enter the flight id or 'find' to lookup the flight id. \n")
                userinput = userinputraw.strip().lower()

                if userinput == "find":
                    #TODO: create a search by details
                    pass
                elif userinput.isnumeric():
                    flight = service.getFlight(int(userinput))
                else:
                    print("That was not a valid input. Flight ids are numeric only. \n")
                    continue

                #TODO: this can be improved on, join the destinations and pilotAssignments in the query to add here.
                if flight:
                    print(f"Flight: {flight.id} \n"
                          f"Status: {flight.status} \n"
                          f"Route: {flight.originAirport} to {flight.destinationAirport} \n"
                          f"Scheduled Departure: {flight.scheduledDepart} \n"
                          f"Scheduled Arrival: {flight.scheduledArrive} \n")
                    break
                else:
                    print(f"No flight found with id: {userinput}")
                    break


        elif userinput == "2":
            pass
        elif userinput == "3":
            continueInput = True
            origin = None
            destination = None
            status = None
            scheduledDepart = None
            scheduledArrive = None
            actualDepart = None
            actualArrive = None
            while continueInput:
                userinputraw = input("Please input the following details: \n"
                                     "What is the airport code for the flights origin? \n")

                if userinputraw.strip().lower() == "back":
                    continueInput = False

                userinput = userinputraw.strip().upper()

                if destinationService.destinationExists(userinput):
                    origin = destinationService.getDestination(userinput).airportId
                    break
                else:
                    continue

            while continueInput:
                userinputraw = input("What is the airport code for the flights destination? \n")

                if userinputraw.strip().lower() == "back":
                    continueInput = False

                userinput = userinputraw.strip().upper()

                if destinationService.destinationExists(userinput):
                    destination = destinationService.getDestination(userinput).airportId
                    break
                else:
                    continue

            while continueInput:
                userinputraw = input("Does this flight have a schedule yet? Y/N \n")
                userinput = userinputraw.strip().lower()

                if userinput == "back":
                    continueInput = False
                elif userinput == "n":
                    break
                elif userinput == "y":
                    status = "Scheduled"

                    scheduledDepart = ask_for_datetime("departure")
                    scheduledArrive = ask_for_datetime("arrival")

                flightService.addFlight(status=status,
                                        originAirport=origin,
                                        destinationAirport=destination,
                                        scheduledDepart=scheduledDepart,
                                        scheduledArrive=scheduledArrive,
                                        actualDepart=actualDepart,
                                        actualArrive=actualArrive
                                        )

                print("Flight successfully added!")
                continueInput = False

        elif userinput == "4":
            while True:
                userinputraw = input("Please enter the flight id to delete or 'find' to lookup the flight id. \n")
                userinput = userinputraw.strip().lower()

                if userinput == "find":
                    # TODO: create a search by details
                    pass

                if userinput == "back":
                    break

                #TODO: add an are you sure option that shows what is being deleted.
                if userinput.isnumeric():
                    flightService.deleteFlight(int(userinput))
                    print(f"Flight with id {userinput} has been deleted.")
                else:
                    print("That is not a valid flight id.")


def assignPilot():
    pass

def viewPilotSchedule():
    pass

def destinationMenu(service: DestinationService):
    print("Destination Information \n")
    while True:
        userinput = input("Would you like to: \n"
                          "1. View a destinations information \n"
                          "2. Update a destinations information \n"
                          "3. Add a destination \n"
                          "4. Delete a destination \n"
                          "* input 'back' to return to main menu * \n")

        if userinput.strip().lower() == "1":
            airportId = input("Please enter the airport code for the destination you would like to view. \n")
            if airportId.strip().lower() == "back":
                continue

            airportId = airportId.strip().upper()
            destination = service.getDestination(airportId)

            if destination:
                print(f"Airport: {destination.airportName} ({destination.airportId}) "
                      f"in {destination.city}, {destination.country}, {destination.continent}.")
            else:
                print(f"No destination found with airport code {airportId}\n")

        elif userinput.strip().lower() == "2":
            # TODO: add update call
            pass
        elif userinput.strip().lower() == "3":
            print("please answer the following questions regarding the new destination, "
                  "or input 'back' to return to the destination menu.")

            airportId = input("What is the Id for this airport? ex. LHR for London Heathrow \n")
            if airportId.strip().lower() == "back":
                continue
            else:
                airportId = airportId.strip().upper()

            airportName = input("What is the name of this airport? \n")
            if airportName.strip().lower() == "back":
                continue
            else:
                airportName = airportName.strip().lower()

            while True:
                continent = input("In what continent is this airport? \n"
                                     "North America \n"
                                     "South America \n"
                                     "Europe \n"
                                     "Africa \n"
                                     "Asia \n"
                                     "Oceania \n"
                                     "Antarctica \n")

                if continent.strip().lower() == "back":
                    break
                elif (continent.strip().lower() != "north america"
                      and continent.strip().lower() != "south america"
                      and continent.strip().lower() != "europe"
                      and continent.strip().lower() != "africa"
                      and continent.strip().lower() != "asia"
                      and continent.strip().lower() != "oceania"
                      and continent.strip().lower() != "antarctica"):
                    print("That is not a valid continent. Please see the below valid continents: \n"
                          "North America \n"
                          "South America \n"
                          "Europe \n"
                          "Africa \n"
                          "Asia \n"
                          "Oceania \n"
                          "Antarctica \n")
                    continue
                else:
                    continent = continent.strip().lower()
                    break

            country = input("Please enter the country. \n")
            if country.strip().lower() == "back":
                continue
            else:
                country = country.strip().lower()

            city = input("Please enter the city. \n")
            if city.strip().lower() == "back":
                continue
            else:
                city = city.strip().lower()

            try:
                destinationRepo.add(
                    airportId=airportId,
                    airportName=airportName.title(),
                    continent=continent.title(),
                    country=country.title(),
                    city=city.title()
                )
            except:
                print("There was an error in creating that destination.")


        elif userinput.strip().lower() == "4":
            pass

        elif userinput.strip().lower() == "back":
            return

def main():
    userinput = input("Welcome to the Flight Management System. \nStart System? Y/N \n")

    while True:
        if userinput.strip().lower() == "y":
            startRepositories()
            break
        elif userinput.strip().lower() == "n":
            print("Closing System")
            return
        else:
            userinput = input("Please enter either Y or N \n")

    while True:
        print("Main Menu: \n"
              "1. Flights \n"
              "2. Pilots \n"
              "3. Destinations \n")

        userinput = input("Please input your command number, or 'exit' to close the system \n")

        if userinput.strip().lower() == "exit":
            return
        elif userinput.strip().lower() == "1":
            flightMenu(flightService)
        elif userinput.strip().lower() == "2":
            viewPilotSchedule()
        elif userinput.strip().lower() == "3":
            destinationMenu(destinationService)

main()

# if __name__ == "__main__":
#     main()
