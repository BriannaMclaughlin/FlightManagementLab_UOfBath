from datetime import datetime

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
        except ValueError:
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
                    elif destinationService.destination_exists(origin.strip().upper()):
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
                    elif destinationService.destination_exists(destination.strip().upper()):
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
                        if destinationService.destination_exists(origin.strip().upper()) is False:
                            print(f"There is no airport in our system with id {origin.strip().upper()}. \n"
                                  f"Please try again, or go back and add a new destination to the system. \n")
                            continue

                    while True:
                        destination = input("Please enter the id for the destination airport: ")

                        if destination.strip().lower() == "back":
                            break

                        if destinationService.destination_exists(origin.strip().upper()) is False:
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


def flight_menu():
    print("Flight Information \n")
    while True:
        user_input_raw = input("Would you like to: \n"
                          "1. View a flights information \n"
                          "2. Update a flights information \n"
                          "3. Add a flight \n"
                          "4. Delete a flight \n"
                          "* input 'back' to return to main menu * \n")

        user_input = user_input_raw.strip().lower()

        if user_input == "back":
            return

        if user_input == "1":
            while True:
                flight_details = None
                user_input_raw = input("Please enter the flight id or 'find' to lookup the flight id. \n")
                user_input = user_input_raw.strip().lower()

                if user_input == "back":
                    break
                elif user_input == "find":
                    print(find_helper("flight"))
                    continue
                elif user_input.isnumeric():
                    if flightService.flight_exists(int(user_input)):
                        flight_details = flightService.get_flight_details(int(user_input))
                    else:
                        print("That flight id does not exist.")
                else:
                    print("That was not a valid input. Flight ids are numeric only. \n")
                    continue

                if flight_details is not None:
                    print(flightService.flight_details_to_string(flight_details))
                    break
                else:
                    print(f"No flight found with id: {user_input}")
                    break


        elif user_input == "2":
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
                    if flightService.flight_exists(int(user_input.strip())):
                        flight_id = int(user_input)
                        break
                    else:
                        print("That flight id does not exist.")
                        continue
                else:
                    print("That is not a valid input")
                    continue

            flight = flightService.get_flight(flight_id)
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
                    break
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
                    break
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
                    break
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
            flight_details = flightService.get_flight_details(flight_id)

            if status == "In Flight":
                if flight.actual_depart is not None or actual_depart is not None:
                    if len(flight_details.pilots) > 0 or len(pilots) > 0:
                        pass
                    else:
                        print(f"The status of Flight {flight_id} cannot be updated to 'In Flight' "
                              f"without a pilot assigned.")
                        return
                else:
                    print(f"The status of Flight {flight_id} cannot be updated to 'In Flight' "
                          f"without an actual departure time. \n")
                    return
            elif status == "Completed":
                if (flight.actual_depart is not None or actual_depart is not None) \
                        and (flight.actual_arrive is not None or actual_arrive is not None):
                    if len(flight.pilots) > 0 or len(pilots) > 0:
                        pass
                    else:
                        print(f"The status of Flight {flight_id} cannot be updated to 'Completed' "
                              f"without a pilot assigned. \n")
                        return
                else:
                    print(f"The status of Flight {flight_id} cannot be updated to 'Completed' "
                          f"without an actual departure and arrival time. \n")
                    return


            if status is not None:
                kwargs["status"] = status
            if scheduled_depart is not None:
                kwargs["scheduled_depart"] = scheduled_depart
            if scheduled_arrive is not None:
                kwargs["scheduled_arrive"] = scheduled_arrive
            if actual_depart is not None:
                kwargs["actual_depart"] = actual_depart
            if actual_arrive is not None:
                kwargs["actual_arrive"] = actual_arrive

            if len(kwargs) > 0:
                updated = flightService.update_flight(flight_id, **kwargs)
                if updated:
                    print(f"Flight details for flight {flight_id} have been successfully updated. ✅ \n")
                    if status == "Completed":
                        updated_flight = flightService.get_flight(flight_id)
                        updated_flight_details = flightService.get_flight_details(flight_id)
                        flight_delta = updated_flight.actual_arrive - updated_flight.actual_depart
                        flight_hours = int(flight_delta.total_seconds() / 3600)
                        for pilot_info in updated_flight_details.pilots:
                            pilot = pilotService.get_pilot(pilot_id=pilot_info["id"])
                            hours_added = pilotService.add_flight_hours(pilot.id, flight_hours)
                            if hours_added:
                                print(f"{pilot.rank} {pilot.first_name} {pilot.last_name}'s experience hours have been "
                                      f"increased by {str(flight_hours)} hour(s). \n")
                            else:
                                print(f"An error has occurred and the flight hours could not be added to {pilot.rank} "
                                      f"{pilot.first_name} {pilot.last_name}'s experience hours. \n "
                                      f"Please attempt to update their hours directly.")

                else:
                    print(f"An error has occurred and flight {flight_id} has NOT been updated. \n")

            pilots_assigned = 0
            for pilot in pilots:
                if pilotService.check_hours(pilot, flight):
                    assigned = flightAssignmentService.assign_pilot_to_flight(flight_id=flight_id, pilot_id=pilot)
                    if assigned:
                        pilots_assigned += 1

            if pilots_assigned > 0:
                print(f"{pilots_assigned} pilot(s) successfully assigned to flight {flight_id}. ✅ \n")
            elif len(kwargs) == 0:
                print(f"No details have been inputted to update flight {flight_id}")


        elif user_input == "3":
            continue_input = True
            origin = None
            destination = None
            status = None
            scheduled_depart = None
            scheduled_arrive = None
            actual_depart = None
            actual_arrive = None
            print("Please input the following details: \n")
            while continue_input:
                user_input_raw = input("What is the airport code for the flights origin? \n")

                if user_input_raw.strip().lower() == "back":
                    continue_input = False
                elif user_input_raw.strip().lower() == "find":
                    print(find_helper("destination"))
                    continue

                user_input = user_input_raw.strip().upper()

                if destinationService.destination_exists(user_input):
                    origin = destinationService.get_destination(user_input).airport_id
                    break
                else:
                    print(f"There is no airport with an id of {user_input} in the system. "
                          f"Please try another id, or add your chosen airport to the system first.")
                    continue

            while continue_input:
                user_input_raw = input("What is the airport code for the flights destination? \n")

                if user_input_raw.strip().lower() == "back":
                    continue_input = False
                elif user_input_raw.strip().lower() == "find":
                    print(find_helper("destination"))
                    continue

                user_input = user_input_raw.strip().upper()

                if destinationService.destination_exists(user_input):
                    destination = destinationService.get_destination(user_input).airport_id
                    break
                else:
                    print(f"There is no airport with an id of {user_input} in the system. "
                          f"Please try another id, or add your chosen airport to the system first.")
                    continue

            while continue_input:
                #TODO: either figure out a way to find a flight without a schedule or remove this option.
                user_input_raw = input("Does this flight have a schedule yet? Y/N \n")
                userinput = user_input_raw.strip().lower()

                if userinput == "back":
                    break
                elif userinput == "y":
                    status = "Scheduled"

                    scheduled_depart = ask_for_datetime("departure")
                    scheduled_arrive = ask_for_datetime("arrival")
                elif userinput != "n":
                    break

                flightService.add_flight(status=status,
                                        origin_airport=origin,
                                        destination_airport=destination,
                                        scheduled_depart=scheduled_depart,
                                        scheduled_arrive=scheduled_arrive,
                                        actual_depart=actual_depart,
                                        actual_arrive=actual_arrive
                                        )

                print("Flight successfully added!")
                continue_input = False

        elif user_input == "4":
            while True:
                user_input_raw = input("Please enter the flight id to delete or 'find' to lookup the flight id. \n")
                user_input = user_input_raw.strip().lower()

                if user_input == "find":
                    print(find_helper("flight"))
                    continue

                if user_input == "back":
                    break

                if user_input.isnumeric():
                    if flightService.flight_exists(int(user_input)):
                        flight_details = flightService.get_flight_details(int(user_input))
                        print(flightService.flight_details_to_string(flight_details))
                        is_sure = input("Are you sure you wish to delete the above flight? Y/N: ")
                        if is_sure.strip().lower() == "y":
                            flightService.delete_flight(int(user_input))
                            print(f"Flight with id {user_input} has been deleted.")
                            break
                        else:
                            print("Nothing has been deleted.")
                            continue
                    else:
                        print(f"There is no flight with id {user_input}")
                else:
                    print("That is not a valid flight id.")

def pilot_menu(service: PilotService):
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
                    if pilot.active:
                        active = "Active"
                    else:
                        active = "Inactive"
                    print(f"Pilot: {pilot.id} ({active})\n"
                          f"Rank: {pilot.rank} \n"
                          f"Name: {pilot.first_name} {pilot.last_name} \n"
                          f"License Number: {pilot.license_number} \n"
                          f"Flight Hours: {pilot.experience_hours} \n"
                          f"Home Airport: {destinationService.get_destination(pilot.home_airport).airport_name}"
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
                    if pilotService.pilot_exists(int(user_input.strip())):
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
                        if destinationService.destination_exists(user_input.strip().upper()):
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

            if len(kwargs) > 0:
                updated = pilotService.update_pilot(pilot_id=pilot_id, **kwargs)
                if updated:
                    print(f"Pilot {pilot_id} has been successfully updated. ✅ \n")
                else:
                    print(f"There was an error in updating pilot {pilot_id}. ✅ \n")
            else:
                print("No details were chosen to be updated.")


        elif user_input == "3":
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

            while rank is None:
                user_input_raw = input("Rank: ")

                if user_input_raw.strip().lower() == "back": return
                elif user_input_raw.strip().title() in valid_rank:
                    rank = user_input_raw.strip().title()
                else:
                    print("That is not a valid rank. Please enter either Captain, First Officer or Second Officer.")


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

                airport = destinationService.get_destination(user_input_raw.strip().upper())

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
                    if service.pilot_exists(int(user_input.strip())):
                        pilot_id = int(user_input.strip())
                        #TODO: change this to now, after adding more flight assignments
                        start_date = datetime(2025, 10, 1)
                        flights = flightAssignmentService.get_schedule_for_pilot(pilot_id=pilot_id, start_date=start_date)
                        if len(flights) > 0:
                            for flight in flights:
                                print(f"ID {flight.id}: {flight.status} {flight.origin_airport} -> "
                                      f"{flight.destination_airport} scheduled to depart at {flight.scheduled_depart}"
                                      f" and arrive at {flight.scheduled_arrive}")
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
                    if pilotService.pilot_exists(int(user_input.strip())):
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
                    if flightService.flight_exists(int(user_input.strip())):
                        flight = flightService.get_flight(int(user_input.strip()))
                        if pilotService.check_hours(pilot_id, flight) is False:
                            break
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
                assigned = flightAssignmentService.assign_pilot_to_flight(pilot_id=pilot_id, flight_id=flight_id)
                if assigned:
                    print(f"Pilot {pilot_id} has been successfully assigned to flight {flight_id}. ✅ \n")

        elif user_input == "6":
            while True:
                user_input_raw = input("Please enter the pilot id to delete or 'find' to lookup the flight id. \n")
                userinput = user_input_raw.strip().lower()

                if userinput == "find":
                    print(find_helper("pilot"))
                    continue

                if userinput == "back":
                    break

                if userinput.isnumeric():
                    if pilotService.pilot_exists(int(userinput)):
                        while True:
                            retire_raw = input("Would you like retire this pilot from active service instead of deleting their "
                                               "data? Y/N: ")
                            if retire_raw.strip().lower() == "back":
                                return
                            elif retire_raw.strip().lower() == "y":
                                updated = pilotService.update_pilot(int(userinput), active=False)
                                if updated:
                                    print(f"Pilot {userinput} has been retired from active service.")
                                    return
                                else:
                                    print(f"An error has occurred and {userinput} has not been updated.")
                                    return
                            elif retire_raw.strip().lower() == "n":
                                pilot = pilotService.get_pilot(int(userinput))
                                print(f"id: {pilot.id} -> {pilot.rank} {pilot.first_name} {pilot.last_name}")
                                is_sure = input("Are you sure you with to delete the above pilot? Y/N")
                                if is_sure.strip().lower() == "y":
                                    delete = pilotService.delete_pilot(int(userinput))
                                    if delete:
                                        print(f"Flight with id {userinput} has been deleted.")
                                        break
                                    else:
                                        print(f"An error has occurred and Pilot {userinput} has NOT been deleted.")
                                        break
                                else:
                                    print(f"Pilot with id {pilot.id} has NOT been deleted.")
                            else:
                                print("That is not a valid input. Please input y or n")
                                continue
                    else:
                        print(f"There is no pilot with an id of {userinput}")

def destination_menu(service: DestinationService):
    print("Destination Information \n")
    while True:
        userinput = input("Would you like to: \n"
                          "1. View a destinations information \n"
                          "2. Update a destinations information \n"
                          "3. Add a destination \n"
                          "4. Delete a destination \n"
                          "* input 'back' to return to main menu * \n")

        if userinput.strip().lower() == "1":
            while True:
                airport_id = input("Please enter the airport code for the destination you would like to view or 'find'. \n")
                if airport_id.strip().lower() == "back":
                    break

                if airport_id.strip().lower() == "find":
                    print(find_helper("destination"))
                    continue

                airport_id = airport_id.strip().upper()

                if destinationService.destination_exists(airport_id):
                    destination = service.get_destination(airport_id)
                else:
                    print(f"No destination found with airport code {airport_id}\n")
                    continue

                if destination:
                    print(f"Airport: {destination.airport_name} ({destination.airport_id}) "
                          f"in {destination.city}, {destination.country}. \n")
                    break


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
                    if service.destination_exists(user_input.strip().upper()):
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

            if len(kwargs) > 0:
                updated = destinationService.update(airport_id=airport_id, **kwargs)
                if updated:
                    print(f"Airport {airport_id} has been successfully updated. ✅ \n")
                else:
                    print(f"An error has occurred and airport {airport_id} has NOT been updated. \n")
            else:
                print(f"No details were chosen to be updated for airport {airport_id}.")


        elif userinput.strip().lower() == "3":
            print("please answer the following questions regarding the new destination, "
                  "or input 'back' to return to the destination menu.")

            airport_id = input("What is the Id for this airport? ex. LHR for London Heathrow \n")
            if airport_id.strip().lower() == "back":
                continue
            else:
                airport_id = airport_id.strip().upper()

            airport_name = input("What is the name of this airport? \n")
            if airport_name.strip().lower() == "back":
                continue
            else:
                airport_name = airport_name.strip().lower()


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
                    airport_id=airport_id,
                    airport_name=airport_name.title(),
                    country=country.title(),
                    city=city.title()
                )
                print(f"Airport with id {airport_id} has been successfully added.")
            except Exception as e:
                print(f"There was an error in creating that destination: {e}")


        elif userinput.strip().lower() == "4":
            while True:
                user_input_raw = input("Please enter the airport id to delete or 'find' to lookup the airport id. \n")
                user_input = user_input_raw.strip().lower()

                if user_input == "find":
                    print(find_helper("destination"))
                    continue

                if user_input == "back":
                    break

                user_input = user_input.upper()

                if destinationService.destination_exists(user_input):
                        while True:
                                destination = destinationService.get_destination(user_input)
                                print(f"Airport id: {destination.airport_id} -> {destination.airport_name}, {destination.city},"
                                      f" {destination.country}")
                                is_sure = input("Are you sure you with to delete the above destination? Y/N: ")
                                if is_sure.strip().lower() == "y":
                                    delete = destinationService.delete(destination.airport_id)
                                    if delete:
                                        print(f"Destination with airport id {destination.airport_id} has been deleted.")
                                        break
                                    else:
                                        print(f"An error has occurred and the destination with airport id "
                                              f"{destination.airport_id} has NOT been deleted.")
                                        break
                                elif is_sure.strip().lower() == "n":
                                    print(f"Destination with airport id {destination.airport_id} has NOT been deleted.")
                                else:
                                    print("That is not a valid input. Please input y or n")
                                    continue

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
            flight_menu()
        elif userinput.strip().lower() == "2":
            pilot_menu(pilotService)
        elif userinput.strip().lower() == "3":
            destination_menu(destinationService)

main()

# if __name__ == "__main__":
#     main()
