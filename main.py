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

valid_status = ["Scheduled", "Delayed", "Completed", "In Flight"]
valid_rank = ["Captain", "First Officer", "Second Officer"]

#TODO: change all variables and methods to snake case because python. Only classes should be camel case

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

        time_raw = input(f"Enter {label} time (HH:MM): ")
        try:
            hour, minute = map(int, time_raw.split(":"))
            if not (0 <= hour <= 23 and 0 <= minute <= 59):
                raise ValueError
        except Exception:
            print("Invalid time")
            continue

        return datetime(year, month, day, hour, minute)

def find_helper(label: str) -> None | str:
    #TODO: confirm this works for multiple airports in a city, and clean up how the result is shown
    if label == "destination":
        city_raw = input("Please enter a city to search for airports in: ")

        if city_raw.strip().lower() == "back":
            return None
        else:
            return  destinationService.find_by_city(city_raw.strip().title())
    elif label == "pilot":
        last_name_raw = input("Please enter the last name for the pilot you wish to find: ")

        if last_name_raw.strip().lower() == "back":
            return None
        else:
            return pilotService.find_by_last_name(last_name_raw.strip().title())
    elif label == "flight":
        while True:
            user_input = input("Would you like to search by: \n"
                               "1. Origin Airport Id \n"
                               "2. Destination Airport Id \n"
                               "3. Origin and Destination Airport Id \n")

            if user_input.strip().lower() == "back":
                return None
            elif user_input.strip() == "1":
                while True:
                    origin = input("Please enter the id for the origin airport: ")

                    if origin.strip().lower() == "back":
                        break
                    elif destinationService.destinationExists(origin.strip().upper()):
                        print("Please enter a date range for the search.")
                        print("Start Date: ")
                        start = ask_for_datetime("start")
                        print("End Date: ")
                        end = ask_for_datetime("end")
                        return flightService.find_by_origin(origin.strip().upper(), start, end)
                    else:
                        print(f"There is no airport in our system with id {origin.strip().upper()}. \n"
                              f"Please try again, or go back and add a new destination to the system. \n")

            elif user_input.strip() == "2":
                while True:
                    destination = input("Please enter the id for the destination airport: ")

                    if destination.strip().lower() == "back":
                        break
                    elif destinationService.destinationExists(destination.strip().upper()):
                        print("Please enter a date range for the search.")
                        print("Start Date: ")
                        start = ask_for_datetime("start")
                        print("End Date: ")
                        end = ask_for_datetime("end")
                        return flightService.find_by_destination(destination.strip().upper(), start, end)
                    else:
                        print(f"There is no airport in our system with id {destination.strip().upper()}. \n"
                              f"Please try again, or go back and add a new destination to the system. \n")

            elif user_input.strip() == "3":
                while True:
                    while True:
                        origin = input("Please enter the id for the origin airport: ")

                        if origin.strip().lower() == "back":
                            break
                        if destinationService.destinationExists(origin.strip().upper()) is False:
                            print(f"There is no airport in our system with id {origin.strip().upper()}. \n"
                                  f"Please try again, or go back and add a new destination to the system. \n")
                            continue

                    while True:
                        destination = input("Please enter the id for the destination airport: ")

                        if destination.strip().lower() == "back":
                            break

                        if destinationService.destinationExists(origin.strip().upper()) is False:
                            print(f"There is no airport in our system with id {origin.strip().upper()}. \n"
                                  f"Please try again, or go back and add a new destination to the system. \n")
                            continue

                    print("Please enter a date range for the search.")
                    print("Start Date: ")
                    start = ask_for_datetime("start")
                    print("End Date: ")
                    end = ask_for_datetime("end")
                    return flightService.find_by_destination(destination.strip().upper(), start, end)

            else:
                print("That is not a valid input. Please input 1, 2 or 3.")
                continue


    return None


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

                if userinput == "back":
                    break
                elif userinput == "find":
                    print(find_helper("flight"))
                    continue
                elif userinput.isnumeric():
                    if flightService.flightExists(int(userinput)):
                        flight_details = flightService.get_flight_details(int(userinput))
                    else:
                        print("That flight id does not exist.")
                else:
                    print("That was not a valid input. Flight ids are numeric only. \n")
                    continue

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
            #TODO: status can only change to complete if actual depart and arrive are completed,
            # then flight hours must be added to each pilot.
            flight_id = None
            status = None
            scheduled_depart = None
            scheduled_arrive = None
            actual_depart = None
            actual_arrive = None
            pilots = []

            while True:
                user_input = input("Please enter the id for the flight you would like to update or 'find': ")

                if user_input.strip().lower() == "back":
                    return
                elif user_input.strip().lower() == "find":
                    print(find_helper("flight"))
                    continue
                elif user_input.strip().isnumeric():
                    if flightService.flightExists(int(user_input.strip())):
                        flight_id = int(user_input)
                        break
                    else:
                        print("That flight id does not exist.")
                        continue
                else:
                    print("That is not a valid input")
                    continue

            print("For each of the below items, input Y to update or N to skip: \n")

            while True:
                user_input=input("Flight Status: ")
                if user_input.strip().lower() == "back":
                    return
                elif user_input.strip().lower() == "y":
                    user_input = input("Please enter the new status: ")

                    if user_input.strip().lower() == "back":
                        return
                    elif user_input.strip().lower().title() in valid_status:
                        status = user_input.strip().title()
                        break
                    else:
                        print("That is not a valid status. Please enter Scheduled, Delayed, In Flight or Completed")
                        continue
                elif user_input.strip().lower() == "n" or user_input.strip().lower() == "":
                    break
                else:
                    print("That is not a valid input. Please enter either Y or N")
                    continue

            while True:
                user_input=input("Scheduled Departure: ")
                if user_input.strip().lower() == "back":
                    return
                elif user_input.strip().lower() == "y":
                    scheduled_depart = ask_for_datetime("depart")
                elif user_input.strip().lower() == "n" or user_input.strip().lower() == "":
                    break
                else:
                    print("That is not a valid input. Please enter either Y or N")
                    continue

            while True:
                user_input = input("Scheduled Arrival: ")
                if user_input.strip().lower() == "back":
                    return
                elif user_input.strip().lower() == "y":
                    scheduled_arrive = ask_for_datetime("arrive")
                    break
                elif user_input.strip().lower() == "n" or user_input.strip().lower() == "":
                    break
                else:
                    print("That is not a valid input. Please enter either Y or N")
                    continue

            while True:
                user_input = input("Actual Departure: ")
                if user_input.strip().lower() == "back":
                    return
                elif user_input.strip().lower() == "y":
                    actual_depart = ask_for_datetime("depart")
                elif user_input.strip().lower() == "n" or user_input.strip().lower() == "":
                    break
                else:
                    print("That is not a valid input. Please enter either Y or N")
                    continue

            while True:
                user_input = input("Actual Arrival: ")
                if user_input.strip().lower() == "back":
                    return
                elif user_input.strip().lower() == "y":
                    actual_arrive = ask_for_datetime("arrive")
                elif user_input.strip().lower() == "n" or user_input.strip().lower() == "":
                    break
                else:
                    print("That is not a valid input. Please enter either Y or N")
                    continue

            while True:
                user_input = input("Pilots Assigned: ")
                if user_input.strip().lower() == "back":
                    return
                elif user_input.strip().lower() == "y":
                    num_pilots_raw = input("How many pilots would you like to assign? ")
                    if num_pilots_raw.strip().lower() == "back":
                        return
                    elif num_pilots_raw.strip().isnumeric():
                        num_pilots = int(num_pilots_raw.strip())

                        for num in range(num_pilots):
                            while True:
                                print("You can input 'find' to search for pilot ids.")
                                pilot_id_raw = input(f"{num+1}. Pilot Id: ")
                                if pilot_id_raw.strip().lower() == "back":
                                    return
                                elif pilot_id_raw.strip().isnumeric():
                                    pilot_id = int(pilot_id_raw.strip())
                                    pilots.append(pilot_id)
                                    break
                                elif pilot_id_raw.strip().lower() == "find":
                                    print(find_helper("pilot"))
                                else:
                                    print("That is not a valid input")
                                    continue
                    else:
                        print("That is not a valid input.")
                        continue

                    break


                elif user_input.strip().lower() == "n" or user_input.strip().lower() == "":
                    break
                else:
                    print("That is not a valid input. Please enter either Y or N")
                    continue

            kwargs = {}

            if status is not None:
                kwargs["status"] = status
            if scheduled_depart is not None:
                kwargs["scheduledDepart"] = scheduled_depart
            if scheduled_arrive is not None:
                kwargs["scheduledArrive"] = scheduled_arrive
            if actual_depart is not None:
                kwargs["actualDepart"] = actual_depart
            if actual_arrive is not None:
                kwargs["actualArrive"] = actual_arrive

            flightService.update_flight(flight_id, **kwargs)

            for pilot in pilots:
                flightAssignmentService.assign_pilot_to_flight(flight_id=flight_id, pilot_id=pilot)


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
                elif userinputraw.strip().lower() == "find":
                    print(find_helper("destination"))
                    continue

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
                elif userinputraw.strip().lower() == "find":
                    print(find_helper("destination"))
                    continue

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
                    print(find_helper("flight"))
                    continue

                if userinput == "back":
                    break

                if userinput.isnumeric():
                    if flightService.flightExists(int(userinput)):
                        print(flightService.get_flight_details(int(userinput)))
                        is_sure = input("Are you sure you wish to delete the above flight? Y/N")
                        if is_sure.strip().lower() == "y":
                            flightService.deleteFlight(int(userinput))
                            print(f"Flight with id {userinput} has been deleted.")
                        else:
                            return
                    else:
                        print(f"There is no flight with id {userinput}")
                else:
                    print("That is not a valid flight id.")

def pilotMenu(service: PilotService):
    print("Pilot Information \n")
    while True:
        user_input_raw = input("Would you like to: \n"
                               "1. View a pilots information ️\n"
                               "2. Update a pilots information \n"
                               "3. Add a pilot 🧑🏽‍✈️\n"
                               "4. View pilot schedule \n" 
                               "5. Add a flight to a pilots schedule \n"
                               "6. Delete a pilot \n"
                             "* input 'back' to return to main menu * \n")

        user_input = user_input_raw.strip().lower()

        if user_input == "back":
            return
        elif user_input == "1":
            while True:
                user_input_raw = input("Please enter the pilot id or 'find' to lookup the pilot id. \n")
                user_input = user_input_raw.strip().lower()

                if user_input == "find":
                    print(find_helper("pilot"))
                    continue
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
                          f"Home Airport: {destinationService.getDestination(pilot.home_airport).airportName}"
                          f" ({pilot.home_airport})\n")
                    break
                else:
                    print(f"No pilot found with id: {user_input}")
                    break

        elif user_input == "2":
            pilot_id = None
            first_name = None
            last_name = None
            rank = None
            license_number = None
            flight_hours = None
            home_airport = None
            active = None

            while True:
                user_input = input("Please enter the id for the pilot you would like to update or 'find': ")

                if user_input.strip().lower() == "back":
                    return
                elif user_input.strip().lower() == "find":
                    print(find_helper("pilot"))
                    continue
                elif user_input.strip().isnumeric():
                    if pilotService.pilotExists(int(user_input.strip())):
                        pilot_id = int(user_input)
                        break
                    else:
                        print("That pilot id does not exist.")
                else:
                    print("That is not a valid input")
                    continue

            print("For each of the below items, input Y to update or N to skip: \n")

            while True:
                user_input=input("First Name: ")
                if user_input.strip().lower() == "back":
                    return
                elif user_input.strip().lower() == "y":
                    user_input = input("Please enter the new first name: ")

                    if user_input.strip().lower() == "back":
                        return
                    else:
                        first_name = user_input.strip().title()
                        break
                elif user_input.strip().lower() == "n" or user_input.strip().lower() == "":
                    break
                else:
                    print("That is not a valid input. Please enter either Y or N")
                    continue

            while True:
                user_input=input("Last Name: ")
                if user_input.strip().lower() == "back":
                    return
                elif user_input.strip().lower() == "y":
                    user_input = input("Please enter the new last name: ")

                    if user_input.strip().lower() == "back":
                        return
                    else:
                        last_name = user_input.strip().title()
                        break
                elif user_input.strip().lower() == "n" or user_input.strip().lower() == "":
                    break
                else:
                    print("That is not a valid input. Please enter either Y or N")
                    continue

            while True:
                user_input=input("Rank: ")
                if user_input.strip().lower() == "back":
                    return
                elif user_input.strip().lower() == "y":
                    user_input = input("Please enter the new rank: ")

                    if user_input.strip().lower() == "back":
                        return
                    elif user_input.strip().lower().title() in valid_rank:
                        rank = user_input.strip().title()
                        break
                    else:
                        print("That is not a valid rank. Please enter either Captain, First Officer or Second Officer.")
                elif user_input.strip().lower() == "n" or user_input.strip().lower() == "":
                    break
                else:
                    print("That is not a valid input. Please enter either Y or N")
                    continue

            while True:
                user_input=input("Home Airport: ")
                if user_input.strip().lower() == "back":
                    return
                elif user_input.strip().lower() == "y":
                    user_input = input("Please enter the new home airport: ")

                    if user_input.strip().lower() == "back":
                        return
                    else:
                        if destinationService.destinationExists(user_input.strip().upper()):
                            home_airport = user_input.strip().upper()
                            break
                        else:
                            print("That airport does not exist in our system. \n"
                                  "Please try again, or go 'back' and add that airport as a destination first. \n")
                            continue
                elif user_input.strip().lower() == "n" or user_input.strip().lower() == "":
                    break
                else:
                    print("That is not a valid input. Please enter either Y or N")
                    continue

            while True:
                user_input=input("License Number: ")
                if user_input.strip().lower() == "back":
                    return
                elif user_input.strip().lower() == "y":
                    user_input = input("Please enter the new license number: ")

                    if user_input.strip().lower() == "back":
                        return
                    else:
                        license_number = user_input.strip().title()
                        break
                elif user_input.strip().lower() == "n" or user_input.strip().lower() == "":
                    break
                else:
                    print("That is not a valid input. Please enter either Y or N")
                    continue

            while True:
                user_input=input("Flight Hours: ")
                if user_input.strip().lower() == "back":
                    return
                elif user_input.strip().lower() == "y":
                    user_input = input("Please enter the new flight hours: ")

                    if user_input.strip().lower() == "back":
                        return
                    elif user_input.strip().isnumeric():
                        flight_hours = int(user_input.strip())
                        break
                    else:
                        print("That is not a valid input.")
                        continue
                elif user_input.strip().lower() == "n" or user_input.strip().lower() == "":
                    break
                else:
                    print("That is not a valid input. Please enter either Y or N")
                    continue

            while True:
                user_input=input("Active: ")
                if user_input.strip().lower() == "back":
                    return
                elif user_input.strip().lower() == "y":
                    user_input = input("Please enter the 'Y' to mark pilot as active or 'N' to mark as inactive: ")

                    if user_input.strip().lower() == "back":
                        return
                    elif user_input.strip().lower() == "y":
                        active = True
                        break
                    elif user_input.strip().lower() == "n":
                        active = False
                        break
                elif user_input.strip().lower() == "n" or user_input.strip().lower() == "":
                    break
                else:
                    print("That is not a valid input. Please enter either Y or N")
                    continue

            kwargs = {}

            if first_name is not None:
                kwargs["first_name"] = first_name
            if last_name is not None:
                kwargs["last_name"] = last_name
            if rank is not None:
                kwargs["rank"] = rank
            if home_airport is not None:
                kwargs["home_airport"] = home_airport
            if license_number is not None:
                kwargs["license_number"] = license_number
            if flight_hours is not None:
                kwargs["flight_hours"] = flight_hours
            if active is not None:
                kwargs["active"] = active

            pilotService.update_pilot(pilot_id=pilot_id, **kwargs)


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

        elif user_input == "4":
            while True:
                user_input = input("Please enter the id for the pilot who's schedule you wish to view: ")

                if user_input.strip().lower() == "back":
                    return
                elif user_input.strip().lower() == "find":
                    print(find_helper("pilot"))
                    continue
                elif user_input.strip().isnumeric():
                    if service.pilotExists(int(user_input.strip())):
                        pilot_id = int(user_input.strip())
                        #TODO: change this to now, after adding more flight assignments
                        start_date = datetime(2025, 10, 1)
                        flights = flightAssignmentService.get_schedule_for_pilot(pilot_id=pilot_id, start_date=start_date)
                        if len(flights) > 0:
                            for flight in flights:
                                print(f"ID {flight.id}: {flight.status} {flight.originAirport} -> "
                                      f"{flight.destinationAirport} scheduled to depart at {flight.scheduledDepart}"
                                      f" and arrive at {flight.scheduledArrive}")
                            print("\n")
                            break
                        else:
                            print(f"There are currently no flights scheduled for the pilot with id {user_input.strip()}")
                            break
                    else:
                        print(f"There is no pilot with an id of {user_input.strip()}. Please try again.")
                        continue
                else:
                    print("That is not a valid pilot id.")
                    continue

            continue
        elif user_input == "5":
            pilot_id = None
            flight_id = None
            while True:
                user_input = input("Please enter the id for the pilot you would like to assign to a flight or 'find': ")

                if user_input.strip().lower() == "back":
                    return
                elif user_input.strip().isnumeric():
                    if pilotService.pilotExists(int(user_input.strip())):
                        pilot = pilotService.get_pilot(int(user_input.strip()))
                        if pilot.active:
                            pilot_id = int(user_input.strip())
                            break
                        else:
                            print(f"{pilot.rank} {pilot.first_name} {pilot.last_name} is not active. "
                                  f"Please choose an active pilot or update this pilots details first.")
                            continue
                    else:
                        print(f"No pilot with an id of {user_input.strip()} exists. "
                              f"Please try again or input 'find' to search for the pilot.")
                        continue
                elif user_input.strip().lower() == "find":
                    print(find_helper("pilot"))
                    continue
                else:
                    print("That is not a valid input.")
                    continue

            while True:
                user_input = input(f"Please enter the id for the flight you would like to assign to pilot {pilot_id}: ")

                if user_input.strip().lower() == "back":
                    return
                elif user_input.strip().isnumeric():
                    if flightService.flightExists(int(user_input.strip())):
                    #TODO: add some checks that the pilot is available and in the right location
                        flight_id = int(user_input.strip())
                        break
                    else:
                        print(f"There is no flight with an id of {user_input.strip()}")
                        continue
                elif user_input.strip().lower() == "find":
                    print(find_helper("flight"))
                    continue
                else:
                    print("That is not a valid input.")
                    continue

            if pilot_id is not None and flight_id is not None:
                flightAssignmentService.assign_pilot_to_flight(pilot_id=pilot_id, flight_id=flight_id)

        elif user_input == "6":
            while True:
                userinputraw = input("Please enter the pilot id to delete or 'find' to lookup the flight id. \n")
                userinput = userinputraw.strip().lower()

                if userinput == "find":
                    print(find_helper("pilot"))
                    continue

                if userinput == "back":
                    break

                if userinput.isnumeric():
                    if pilotService.pilotExists(int(userinput)):
                        while True:
                            retire_raw = input("Would you like retire this pilot from active service instead of deleting their "
                                               "data? Y/N")
                            if retire_raw.strip().lower() == "back":
                                return
                            elif retire_raw.strip().lower() == "y":
                                pilotService.update_pilot(int(userinput), active=False)
                                break
                            elif retire_raw.strip().lower() == "n":
                                pilot = pilotService.get_pilot(int(userinput))
                                print(f"id: {pilot.id} -> {pilot.rank} {pilot.first_name} {pilot.last_name}")
                                is_sure = input("Are you sure you with to delete the above pilot? Y/N")
                                if is_sure.strip().lower() == "y":
                                    pilotService.delete_pilot(int(userinput))
                                    print(f"Flight with id {userinput} has been deleted.")
                                    break
                                else:
                                    print(f"Pilot with id {pilot.id} has NOT been deleted.")
                            else:
                                print("That is not a valid input. Please input y or n")
                                continue
                    else:
                        print(f"There is no pilot with an id of {userinput}")









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
            airportId = input("Please enter the airport code for the destination you would like to view or 'find'. \n")
            if airportId.strip().lower() == "back":
                continue

            if airportId.strip().lower() == "find":
                print(find_helper("destination"))
                continue

            airportId = airportId.strip().upper()
            destination = service.getDestination(airportId)

            if destination:
                print(f"Airport: {destination.airportName} ({destination.airportId}) "
                      f"in {destination.city}, {destination.country}.")
            else:
                print(f"No destination found with airport code {airportId}\n")

        elif userinput.strip().lower() == "2":
            airport_id = None
            airport_name = None
            country = None
            city = None

            while airport_id is None:
                user_input = input("Please enter the id for the airport you would like to update or 'find': ")

                if user_input.strip().lower() == "back":
                    return
                elif user_input.strip().lower() == "find":
                    print(find_helper("destination"))
                    continue
                else:
                    if service.destinationExists(user_input.strip().upper()):
                        airport_id = user_input.strip().upper()
                    else:
                        print("That airport id does not exist.")


            print("For each of the below items, input Y to update or N to skip: \n")

            while True:
                user_input = input("Airport Name: ")
                if user_input.strip().lower() == "back":
                    return
                elif user_input.strip().lower() == "y":
                    user_input = input("Please enter the new airport name: ")

                    if user_input.strip().lower() == "back":
                        return
                    else:
                        airport_name = user_input.strip().title()
                        break
                elif user_input.strip().lower() == "n" or user_input.strip().lower() == "":
                    break
                else:
                    print("That is not a valid input. Please enter either Y or N")
                    continue

            while True:
                user_input = input("Country: ")
                if user_input.strip().lower() == "back":
                    return
                elif user_input.strip().lower() == "y":
                    user_input = input("Please enter the new country name: ")

                    if user_input.strip().lower() == "back":
                        return
                    else:
                        country = user_input.strip().title()
                        break
                elif user_input.strip().lower() == "n" or user_input.strip().lower() == "":
                    break
                else:
                    print("That is not a valid input. Please enter either Y or N")
                    continue

            while True:
                user_input = input("City: ")
                if user_input.strip().lower() == "back":
                    return
                elif user_input.strip().lower() == "y":
                    user_input = input("Please enter the new city name: ")

                    if user_input.strip().lower() == "back":
                        return
                    else:
                        city = user_input.strip().title()
                        break
                elif user_input.strip().lower() == "n" or user_input.strip().lower() == "":
                    break
                else:
                    print("That is not a valid input. Please enter either Y or N")
                    continue

            kwargs = {}

            if airport_name is not None:
                kwargs["airportName"] = airport_name
            if country is not None:
                kwargs["country"] = country
            if city is not None:
                kwargs["city"] = city

            service.update(airport_id=airport_id, **kwargs)

            #TODO: add is successfully updated.

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
                destinationService.add(
                    airportId=airportId,
                    airportName=airportName.title(),
                    country=country.title(),
                    city=city.title()
                )
            except Exception as e:
                print(f"There was an error in creating that destination: {e}")


        elif userinput.strip().lower() == "4":
            #TODO
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
