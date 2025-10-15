import contextlib
import datetime
import sqlite3

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
                    scheduled_depart INTEGER,
                    scheduled_arrive INTEGER,
                    actual_depart INTEGER,
                    actual_arrive INTEGER,
                    origin_airport_id VARCHAR NOT NULL,
                    destination_airport_id VARCHAR NOT NULL,
                    FOREIGN KEY (origin_airport_id) REFERENCES destinations(airport_id),
                    FOREIGN KEY (destination_airport_id) REFERENCES destinations(airport_id)
                    UNIQUE(origin_airport_id, destination_airport_id, scheduled_depart)
                )
            """)

    def insert_dummy_data(self) -> None:

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
                (status, scheduled_depart, scheduled_arrive, actual_depart, actual_arrive, origin_airport_id, destination_airport_id)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, dummy_flights)
            print(f"✅ Inserted {cursor.rowcount} new flights (existing ones ignored).")

    def get(self, flight_id: int) -> Flight:
        with self.connect() as (db, cursor):
            cursor.execute("SELECT * FROM flights WHERE id=?", (flight_id,))
            row = cursor.fetchone()
            if row is None:
                raise ValueError(f"Flight with id {flight_id} does not exist")

            def parse_dt(value):
                if value is None:
                    return None
                if isinstance(value, datetime.datetime):
                    return value
                try:
                    return datetime.datetime.fromisoformat(value)
                except Exception:
                    return datetime.datetime.strptime(value, "%Y-%m-%d %H:%M")

            return Flight(
                id=row["id"],
                status=row["status"],
                scheduled_depart=parse_dt(row["scheduled_depart"]),
                scheduled_arrive=parse_dt(row["scheduled_arrive"]),
                actual_depart=parse_dt(row["actual_depart"]),
                actual_arrive=parse_dt(row["actual_arrive"]),
                origin_airport=row["origin_airport_id"],
                destination_airport=row["destination_airport_id"])

    def get_flight_details(self, flight_id: int) -> FlightDetails:
        with self.connect() as (db, cursor):
            cursor.execute("""
            SELECT f.id, f.status, f.scheduled_depart, f.scheduled_arrive, f.actual_depart, f.actual_arrive,
            o.airport_id AS origin_id, o.airport_name AS origin_name, o.city AS origin_city, o.country AS origin_country,
            d.airport_id AS destination_id, d.airport_name AS destination_name, d.city AS destination_city,
            d.country AS destination_country
            FROM flights f
            JOIN destinations o ON f.origin_airport_id = o.airport_id
            JOIN destinations d ON f.destination_airport_id = d.airport_id
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
                scheduled_depart=flight_row["scheduled_depart"],
                scheduled_arrive=flight_row["scheduled_arrive"],
                actual_depart=flight_row["actual_depart"],
                actual_arrive=flight_row["actual_arrive"],
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
            (status, scheduled_depart, scheduled_arrive, actual_depart, actual_arrive, origin_airport,
             destination_airport) = (
                flight.status,
                flight.scheduled_depart,
                flight.scheduled_arrive,
                flight.actual_depart,
                flight.actual_arrive,
                flight.origin_airport,
                flight.destination_airport,
            )
        elif {"status", "scheduled_depart", "scheduled_arrive", "actual_depart",
              "actual_arrive", "origin_airport", "destination_airport"} <= kwargs.keys():
            status = kwargs["status"]
            scheduled_depart = kwargs["scheduled_depart"]
            scheduled_arrive = kwargs["scheduled_arrive"]
            actual_depart = kwargs["actual_depart"]
            actual_arrive = kwargs["actual_arrive"]
            origin_airport = kwargs["origin_airport"]
            destination_airport = kwargs["destination_airport"]
        else:
            raise ValueError("Must provide a Flight object or status, scheduled_depart, scheduled_arrive,"
                             "actual_depart, actual_arrive, origin_airport and destination_airport as kwargs")

        with self.connect() as (db, cursor):
            try:
                cursor.execute(
                    "INSERT INTO flights (status, scheduled_depart, scheduled_arrive, actual_depart, "
                    "actual_arrive, origin_airport_id, destination_airport_id) VALUES (?, ?, ?, ?, ?, ?, ?)",
                    (status, scheduled_depart, scheduled_arrive, actual_depart, actual_arrive, origin_airport,
                     destination_airport),
                )
            except Exception as e:
                db.rollback()
                raise e

    def update(self, flight_id: int, **kwargs: object) -> bool:
        allowed_fields = {"status", "scheduled_depart", "scheduled_arrive", "actual_depart", "actual_arrive",
                          "origin_airport", "destination_airport"}
        set_clauses = []
        values = []

        for field, value in kwargs.items():
            if field in allowed_fields:
                set_clauses.append(f"{field}=?")
                values.append(value)

        if not set_clauses:
            raise ValueError("No valid fields provided to update")

        values.append(flight_id)

        with self.connect() as (db, cursor):
            cursor.execute(
                f"UPDATE flights SET {', '.join(set_clauses)} WHERE id=?",
                tuple(values),
            )
            return cursor.rowcount > 0

    def delete(self, flight_id: int) -> None:
        with self.connect() as (db, cursor):
            cursor.execute("DELETE FROM flights WHERE id=?", (flight_id,))

    def find_by_origin(self, origin: str, start: datetime, end: datetime) -> list[Flight]:
        with self.connect() as (db, cursor):
            cursor.execute("""
                SELECT * FROM flights
                WHERE origin_airport_id = ?
                AND scheduled_depart >= ?
                AND scheduled_depart <= ?
            """, (origin, start, end))
            rows = cursor.fetchall()
            return [
                Flight(
                    id=row["id"],
                    status=row["status"],
                    scheduled_depart=row["scheduled_depart"],
                    scheduled_arrive=row["scheduled_arrive"],
                    actual_depart=row["actual_depart"],
                    actual_arrive=row["actual_arrive"],
                    origin_airport=row["origin_airport_id"],
                    destination_airport=row["destination_airport_id"]
                )
                for row in rows
            ]

    def find_by_destination(self, destination: str, start: datetime, end: datetime) -> list[Flight]:
        with self.connect() as (db, cursor):
            cursor.execute("""
                SELECT * FROM flights
                WHERE destination_airport_id = ?
                AND scheduled_depart >= ?
                AND scheduled_depart <= ?
            """, (destination, start, end))
            rows = cursor.fetchall()
            return [
                Flight(
                    id=row["id"],
                    status=row["status"],
                    scheduled_depart=row["scheduled_depart"],
                    scheduled_arrive=row["scheduled_arrive"],
                    actual_depart=row["actual_depart"],
                    actual_arrive=row["actual_arrive"],
                    origin_airport=row["origin_airport_id"],
                    destination_airport=row["destination_airport_id"]
                )
                for row in rows
            ]

    def find_by_origin_and_destination(self, origin: str, destination: str, start: datetime, end: datetime) -> list[Flight]:
        with self.connect() as (db, cursor):
            cursor.execute("""
                SELECT * FROM flights
                WHERE origin_airport_id = ?
                AND destination_airport_id = ?
                AND scheduled_depart >= ?
                AND scheduled_depart <= ?
            """, (origin, destination, start, end))
            rows = cursor.fetchall()
            return [
                Flight(
                    id=row["id"],
                    status=row["status"],
                    scheduled_depart=row["scheduled_depart"],
                    scheduled_arrive=row["scheduled_arrive"],
                    actual_depart=row["actual_depart"],
                    actual_arrive=row["actual_arrive"],
                    origin_airport=row["origin_airport_id"],
                    destination_airport=row["destination_airport_id"]
                )
                for row in rows
            ]