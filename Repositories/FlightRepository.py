import contextlib
import sqlite3
from http import HTTPStatus

from FlightManagementLab_UOfBath.Entities.Destination import Destination
from .Repository import Repository
from ..Entities.Flight import Flight


class FlightRepository(Repository[Flight]):
    def __init__(self, db_path: str) -> None:
        self.db_path = db_path
        self.create_table()

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
                )
            """)

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