from FlightManagementLab_UOfBath.Entities.Destination import Destination
from FlightManagementLab_UOfBath.Repositories.DestinationRepository import DestinationRepository
import sqlite3

from FlightManagementLab_UOfBath.Services.DestinationService import DestinationService

destinationService = DestinationService()

def startRepositories():
    global destinationRepo
    destinationRepo = DestinationRepository("FlightManagementDB.db")

def flightMenu():
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
            pass
        elif userinput == "2":
            pass
        elif userinput == "3":
            pass
        elif userinput == "4":
            pass

def addNewFlight():
    pass

def updateFlight():
    pass

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
        print("Menu: \n"
              "1. View flight information \n"
              "2. Add a new flight \n"
              "3. Update a flight \n"
              "4. Assign a pilot to a flight \n"
              "5. View Pilot schedule \n"
              "6. View/Update Destination Information \n")

        userinput = input("Please input your command number, or 'exit' to close the system \n")

        if userinput.strip().lower() == "exit":
            return
        elif userinput.strip().lower() == "1":
            viewFlightInformation()
        elif userinput.strip().lower() == "2":
            addNewFlight()
        elif userinput.strip().lower() == "3":
            updateFlight()
        elif userinput.strip().lower() == "4":
            assignPilot()
        elif userinput.strip().lower() == "5":
            viewPilotSchedule()
        elif userinput.strip().lower() == "6":
            destinationMenu(destinationService)

main()

# if __name__ == "__main__":
#     main()
