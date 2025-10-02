from datetime import datetime

from FlightManagementLab_UOfBath.Entities.Destination import Destination
from FlightManagementLab_UOfBath.Repositories.DestinationRepository import DestinationRepository
import sqlite3

from FlightManagementLab_UOfBath.Services.DestinationService import DestinationService
from FlightManagementLab_UOfBath.Services.FlightAssignmentService import FlightAssignmentService
from FlightManagementLab_UOfBath.Services.FlightService import FlightService
from FlightManagementLab_UOfBath.Services.PilotService import PilotService

destinationService = DestinationService()
flightService = FlightService()
pilotService = PilotService()
flightAssignmentService = FlightAssignmentService()

#TODO: change all variables and methods to snake case because python. Only classes should be camel case

def start_repositories():
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

def flight_menu(service: FlightService):
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
                flight_details = None
                userinputraw = input("Please enter the flight id or 'find' to lookup the flight id. \n")
                userinput = userinputraw.strip().lower()

                if userinput == "find":
                    #TODO: create a search by details
                    pass
                elif userinput.isnumeric():
                    flight_details = flightService.get_flight_details(int(userinput))
                else:
                    print("That was not a valid input. Flight ids are numeric only. \n")
                    continue

                #TODO: this can be improved on, join the destinations and pilotAssignments in the query to add here.
                if flight_details is not None:
                    to_print = (f"Flight: {flight_details.id} \n"
                          f"Status: {flight_details.status} \n"
                          f"Route: {flight_details.origin.get("city")} ({flight_details.origin.get("airport_id")}) to "
                          f"{flight_details.destination.get("city")} ({flight_details.destination.get("airport_id")}) \n"
                          f"Scheduled Departure: {flight_details.scheduledDepart} \n"
                          f"Scheduled Arrival: {flight_details.scheduledArrive} \n")
                    if flight_details.actualDepart is not None:
                        to_print += f"Actual Departure: {flight_details.actualDepart} \n"
                    if flight_details.actualArrive is not None:
                        to_print += f"Actual Arrival: {flight_details.actualArrive} \n"

                    if len(flight_details.pilots) > 0:
                        to_print += f"Pilots: \n"
                        for pilot in flight_details.pilots:
                            to_print += (f"Id: {pilot.get("id")}, {pilot.get("rank")} {pilot.get("first_name")} "
                                         f"{pilot.get("last_name")} \n")
                    else:
                        to_print += "Pilots to be determined. \n"
                    print(to_print)
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

def pilotMenu(service: PilotService):
    print("Pilot Information \n")
    while True:
        user_input_raw = input("Would you like to: \n"
                             "1. View a pilots information ️\n"
                             "2. Update a pilots information \n" #TODO
                             "3. Add a pilot 🧑🏽‍✈️\n"
                             "4. Add a flight to a pilots schedule \n" #TODO
                             "5. Delete a pilot \n"
                             "* input 'back' to return to main menu * \n")

        user_input = user_input_raw.strip().lower()

        if user_input == "back":
            return
        elif user_input == "1":
            while True:
                user_input_raw = input("Please enter the pilot id or 'find' to lookup the pilot id. \n")
                user_input = user_input_raw.strip().lower()

                if user_input == "find":
                    #TODO: create a search by details
                    pass
                elif user_input.isnumeric():
                    pilot = pilotService.get_pilot(int(user_input))
                else:
                    print("That was not a valid input. Pilot ids are numeric only. \n")
                    continue

                if pilot:
                    print(f"Pilot: {pilot.id} ({pilot.active})\n"
                          f"Rank: {pilot.rank} \n"
                          f"Name: {pilot.first_name} {pilot.last_name} \n"
                          f"License Number: {pilot.license_number} \n"
                          f"Flight Hours: {pilot.experience_hours} \n"
                          f"Home Airport: {pilot.home_airport} \n")
                    break
                else:
                    print(f"No pilot found with id: {user_input}")
                    break

        elif user_input == "2":
            pass
        elif user_input == "3":
            first_name = None
            last_name = None
            license_number = None
            rank = None
            experience_hours = None
            home_airport = None


            user_input_raw = input("Please provide the following details for the new pilot. \n"
                                   "First Name: ")

            if user_input_raw.strip().lower() == "back": return
            else: first_name = user_input_raw.strip()

            user_input_raw = input("Last Name: ")

            if user_input_raw.strip().lower() == "back": return
            else: last_name = user_input_raw.strip()

            user_input_raw = input("License Number: ")

            if user_input_raw.strip().lower() == "back": return
            else: license_number = user_input_raw.strip()

            user_input_raw = input("Rank: ")

            if user_input_raw.strip().lower() == "back": return
            else: rank = user_input_raw.strip().title()


            while experience_hours is None:
                user_input_raw = input("Experience Hours: ")
                if user_input_raw.strip().lower() == "back": return
                elif user_input_raw.strip().isnumeric():
                    experience_hours = int(user_input_raw.strip())
                else:
                    print("That is not a valid input. Please enter a number.")
                    continue

            while home_airport is None:
                user_input_raw = input("Home Airport Id: ")
                if user_input_raw.strip().lower() == "back": return

                airport = destinationService.getDestination(user_input_raw.strip().upper())

                if airport:
                    home_airport = user_input_raw.strip().upper()
                else:
                    print("That is not a valid airport. Please confirm details and  make sure the airport has been "
                          "added to the system destinations before adding to a pilot.")
                    continue

            pilotService.add_pilot(first_name=first_name,
                               last_name=last_name,
                               license_number=license_number,
                               rank=rank,
                               experience_hours=experience_hours,
                               home_airport=home_airport)

            print("Pilot has been successfully added ✅ \n")

        elif user_input == "5":
            while True:
                userinputraw = input("Please enter the pilot id to delete or 'find' to lookup the flight id. \n")
                userinput = userinputraw.strip().lower()

                if userinput == "find":
                    # TODO: create a search by details
                    pass

                if userinput == "back":
                    break

                # TODO: add an are you sure option that shows what is being deleted.
                if userinput.isnumeric():
                    while True:
                        retire_raw = input("Would you like retire this pilot from active service instead of deleting their "
                                           "data? Y/N")
                        if retire_raw.strip().lower() == "back":
                            return
                        elif retire_raw.strip().lower() == "y":
                            pilotService.update_pilot(int(userinput), active=False)
                            break
                        elif retire_raw.strip().lower() == "n":
                            pilotService.delete_pilot(int(userinput))
                            print(f"Flight with id {userinput} has been deleted.")
                            break
                        else:
                            print("That is not a valid input. Please input y or n")
                            continue









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
            flight_menu(flightService)
        elif userinput.strip().lower() == "2":
            pilotMenu(pilotService)
        elif userinput.strip().lower() == "3":
            destinationMenu(destinationService)

main()

# if __name__ == "__main__":
#     main()
