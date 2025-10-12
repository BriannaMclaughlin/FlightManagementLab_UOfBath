import contextlib
import datetime
import sqlite3
from http import HTTPStatus

from FlightManagementLab_UOfBath.Entities.Destination import Destination
from .Repository import Repository
from ..DTOs.FlightDetails import FlightDetails
from ..Entities.Flight import Flight


class FlightRepository(Repository[Flight]):
    def __init__(self, db_path: str) -> None:
        self.db_path = db_path
        self.create_table()
        self.insert_dummy_data()

    @contextlib.contextmanager
    def connect(self):
        # Context manager that yields both the connection and cursor,
        # commits on exit, and closes safely.
        db = sqlite3.connect(self.db_path)
        try:
            db.row_factory = sqlite3.Row
            cursor = db.cursor()
            yield db, cursor
            db.commit()
        except Exception as e:
            db.rollback()
            raise e
        finally:
            db.close()

    # Not using a flight number which specifies the route because some flights may be private
    # and not have a standard route.
    # private flights may be inputted before the schedule has been set, requiring status and schedules to be null
    # actual depart and actual arrive will be nullable for before this is known.
    def create_table(self) -> None:
        with self.connect() as (db, cursor):
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS flights (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    status TEXT,
                    scheduledDepart INTEGER,
                    scheduledArrive INTEGER,
                    actualDepart INTEGER,
                    actualArrive INTEGER,
                    originAirportId VARCHAR NOT NULL,
                    destinationAirportId VARCHAR NOT NULL,
                    FOREIGN KEY (originAirportId) REFERENCES destinations(airportId),
                    FOREIGN KEY (destinationAirportId) REFERENCES destinations(airportId)
                    UNIQUE(originAirportId, destinationAirportId, scheduledDepart)
                )
            """)

    def insert_dummy_data(self) -> None:
        now = datetime.datetime.now()

        dummy_flights = [
            # status, scheduledDepart, scheduledArrive, actualDepart, actualArrive, origin, destination
            ("Scheduled", datetime.datetime(2025, 10, 15, 10, 0), datetime.datetime(2025, 10, 15, 17, 0), None, None,
             "JFK", "LHR"),
            ("Scheduled", datetime.datetime(2025, 10, 17, 8, 0), datetime.datetime(2025, 10, 17, 16, 0), None, None,
             "LAX", "CDG"),
            ("In Flight", datetime.datetime(2025, 10, 12, 5, 0), datetime.datetime(2025, 10, 12, 13, 0),
             datetime.datetime(2025, 10, 12, 5, 0), None, "DXB", "SIN"),
            ("Completed", datetime.datetime(2025, 10, 11, 3, 0), datetime.datetime(2025, 10, 11, 10, 0),
             datetime.datetime(2025, 10, 11, 3, 0), datetime.datetime(2025, 10, 11, 10, 0), "LHR", "JFK"),
            ("Scheduled", datetime.datetime(2025, 11, 25, 21, 30), datetime.datetime(2025, 11, 26, 5, 15), None, None,
             "STN", "LHR"),
            (
            "Scheduled", datetime.datetime(2025, 12, 5, 9, 0), datetime.datetime(2025, 12, 5, 12, 0), None, None, "LHR",
            "CDG"),
            ("Scheduled", datetime.datetime(2025, 12, 10, 22, 45), datetime.datetime(2025, 12, 11, 6, 30), None, None,
             "CDG", "DXB"),
        ]

        with self.connect() as (db, cursor):
            cursor.executemany("""
                INSERT OR IGNORE INTO flights
                (status, scheduledDepart, scheduledArrive, actualDepart, actualArrive, originAirportId, destinationAirportId)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, dummy_flights)
            print(f"✅ Inserted {cursor.rowcount} new flights (existing ones ignored).")

    def get(self, id: int) -> Flight:
        with self.connect() as (db, cursor):
            cursor.execute("SELECT * FROM flights WHERE id=?", (id,))
            row = cursor.fetchone()
            if row is None:
                raise ValueError(f"Flight with id {id} does not exist")
            return Flight(
                id=row["id"],
                status=row["status"],
                scheduledDepart=row["scheduledDepart"],
                scheduledArrive=row["scheduledArrive"],
                actualDepart=row["actualDepart"],
                actualArrive=row["actualArrive"],
                originAirport=row["originAirportId"],
                destinationAirport=row["destinationAirportId"])

    def get_flight_details(self, flight_id: int) -> FlightDetails:
        with self.connect() as (db, cursor):
            cursor.execute("""
            SELECT f.id, f.status, f.scheduledDepart, f.scheduledArrive, f.actualDepart, f.actualArrive,
            o.airportId AS origin_id, o.airportName AS origin_name, o.city AS origin_city, o.country AS origin_country,
            d.airportId AS destination_id, d.airportName AS destination_name, d.city AS destination_city,
            d.country AS destination_country
            FROM flights f
            JOIN destinations o ON f.originAirportId = o.airportId
            JOIN destinations d ON f.destinationAirportId = d.airportId
            WHERE f.id = ?
            """, (flight_id,)
            )
            flight_row = cursor.fetchone()
            if flight_row is None:
                raise ValueError(f"Flight with id {flight_id} does not exist.")

            # get pilots for flight
            cursor.execute("""
            SELECT p.id, p.first_name, p.last_name, p.rank
            FROM pilots p
            JOIN flight_assignment fa ON p.id = fa.pilot_id
            WHERE fa.flight_id = ?
            """, (flight_id,)
            )
            pilots = [dict(row) for row in cursor.fetchall()]

            origin = {
                "airport_id": flight_row["origin_id"],
                "airport_name": flight_row["origin_name"],
                "city": flight_row["origin_city"],
                "country": flight_row["origin_country"]
            }

            destination = {
                "airport_id": flight_row["destination_id"],
                "airport_name": flight_row["destination_name"],
                "city": flight_row["destination_city"],
                "country": flight_row["destination_country"]
            }

            return FlightDetails(
                id=flight_row["id"],
                status=flight_row["status"],
                scheduledDepart=flight_row["scheduledDepart"],
                scheduledArrive=flight_row["scheduledArrive"],
                actualDepart=flight_row["actualDepart"],
                actualArrive=flight_row["actualArrive"],
                origin=origin,
                destination=destination,
                pilots=pilots
            )

    def get_all(self) -> list[Flight]:
        with self.connect() as (db, cursor):
            cursor.execute("SELECT * FROM flights")
            return [Flight(*row) for row in cursor.fetchall()]

    def add(self, flight: Flight | None = None, **kwargs: object) -> None:
        if flight:
            (status, scheduledDepart, scheduledArrive, actualDepart, actualArrive, originAirport,
             destinationAirport) = (
                flight.status,
                flight.scheduledDepart,
                flight.scheduledArrive,
                flight.actualDepart,
                flight.actualArrive,
                flight.originAirport,
                flight.destinationAirport,
            )
        elif {"status", "scheduledDepart", "scheduledArrive", "actualDepart",
              "actualArrive", "originAirport", "destinationAirport"} <= kwargs.keys():
            status = kwargs["status"]
            scheduledDepart = kwargs["scheduledDepart"]
            scheduledArrive = kwargs["scheduledArrive"]
            actualDepart = kwargs["actualDepart"]
            actualArrive = kwargs["actualArrive"]
            originAirport = kwargs["originAirport"]
            destinationAirport = kwargs["destinationAirport"]
        else:
            raise ValueError("Must provide a Flight object or status, scheduledDepart, scheduledArrive,"
                             "actualDepart, actualArrive, originAirport and destinationAirport as kwargs")

        with self.connect() as (db, cursor):
            try:
                cursor.execute(
                    "INSERT INTO flights (status, scheduledDepart, scheduledArrive, actualDepart, "
                    "actualArrive, originAirportId, destinationAirportId) VALUES (?, ?, ?, ?, ?, ?, ?)",
                    (status, scheduledDepart, scheduledArrive, actualDepart, actualArrive, originAirport,
                     destinationAirport),
                )
            except Exception as e:
                db.rollback()
                raise e

    def update(self, id: int, **kwargs: object) -> None:
        allowed_fields = {"status", "scheduledDepart", "scheduledArrive", "actualDepart", "actualArrive",
                          "originAirport", "destinationAirport"}
        set_clauses = []
        values = []

        for field, value in kwargs.items():
            if field in allowed_fields:
                set_clauses.append(f"{field}=?")
                values.append(value)

        if not set_clauses:
            raise ValueError("No valid fields provided to update")

        values.append(id)

        with self.connect() as (db, cursor):
            cursor.execute(
                f"UPDATE flights SET {', '.join(set_clauses)} WHERE id=?",
                tuple(values),
            )

    def delete(self, id: int) -> None:
        with self.connect() as (db, cursor):
            cursor.execute("DELETE FROM flights WHERE id=?", (id,))

    def find_by_origin(self, origin: str, start: datetime, end: datetime) -> list[Flight]:
        with self.connect() as (db, cursor):
            cursor.execute("""
                SELECT * FROM flights
                WHERE originAirportId = ?
                AND scheduledDepart >= ?
                AND scheduledDepart <= ?
            """, (origin, start, end))
            rows = cursor.fetchall()
            return [
                Flight(
                    id=row["id"],
                    status=row["status"],
                    scheduledDepart=row["scheduledDepart"],
                    scheduledArrive=row["scheduledArrive"],
                    actualDepart=row["actualDepart"],
                    actualArrive=row["actualArrive"],
                    originAirport=row["originAirportId"],
                    destinationAirport=row["destinationAirportId"]
                )
                for row in rows
            ]

    def find_by_destination(self, destination: str, start: datetime, end: datetime) -> list[Flight]:
        with self.connect() as (db, cursor):
            cursor.execute("""
                SELECT * FROM flights
                WHERE destinationAirportId = ?
                AND scheduledDepart >= ?
                AND scheduledDepart <= ?
            """, (destination, start, end))
            rows = cursor.fetchall()
            return [
                Flight(
                    id=row["id"],
                    status=row["status"],
                    scheduledDepart=row["scheduledDepart"],
                    scheduledArrive=row["scheduledArrive"],
                    actualDepart=row["actualDepart"],
                    actualArrive=row["actualArrive"],
                    originAirport=row["originAirportId"],
                    destinationAirport=row["destinationAirportId"]
                )
                for row in rows
            ]

    def find_by_origin_and_destination(self, origin: str, destination: str, start: datetime, end: datetime) -> list[Flight]:
        with self.connect() as (db, cursor):
            cursor.execute("""
                SELECT * FROM flights
                WHERE originAirportId = ?
                AND destinationAirportId = ?
                AND scheduledDepart >= ?
                AND scheduledDepart <= ?
            """, (origin, destination, start, end))
            rows = cursor.fetchall()
            return [
                Flight(
                    id=row["id"],
                    status=row["status"],
                    scheduledDepart=row["scheduledDepart"],
                    scheduledArrive=row["scheduledArrive"],
                    actualDepart=row["actualDepart"],
                    actualArrive=row["actualArrive"],
                    originAirport=row["originAirportId"],
                    destinationAirport=row["destinationAirportId"]
                )
                for row in rows
            ]