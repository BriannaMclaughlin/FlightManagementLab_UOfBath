import contextlib
import sqlite3
from http import HTTPStatus

from FlightManagementLab_UOfBath.Entities.Destination import Destination
from .Repository import Repository


class DestinationRepository(Repository[Destination]):
    def __init__(self, db_path: str) -> None:
        self.db_path = db_path
        self.create_table()

    @contextlib.contextmanager
    def connect(self):
        """
        Context manager that yields both the connection and cursor,
        commits on exit, and closes safely.
        """
        db = sqlite3.connect(self.db_path)
        try:
            cursor = db.cursor()
            yield db, cursor
            db.commit()
        except Exception as e:
            db.rollback()
            raise e
        finally:
            db.close()

    def create_table(self) -> None:
        with self.connect() as (db, cursor):
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS destinations (
                    airportId VARCHAR PRIMARY KEY,
                    airportName VARCHAR,
                    continent TEXT,
                    country TEXT,
                    city TEXT
                )
            """)

    def get(self, airportId: str) -> Destination:
        with self.connect() as (db, cursor):
            cursor.execute("SELECT * FROM destinations WHERE airportId=?", (airportId,))
            row = cursor.fetchone()
            if row is None:
                raise ValueError(f"Destination with id {airportId} does not exist")
            return Destination(*row)

    def get_all(self) -> list[Destination]:
        with self.connect() as (db, cursor):
            cursor.execute("SELECT * FROM destinations")
            return [Destination(*row) for row in cursor.fetchall()]

    def add(self, destination: Destination | None = None, **kwargs: object) -> None:
        """
        Add a new destination. Can pass either a Destination object or kwargs.
        Example:
            repo.add(Destination("YYZ", "North America", "Canada", "Toronto"))
        or
            repo.add(airportId="YYZ", continent="North America", country="Canada", city="Toronto")
        """
        if destination:
            airportId, airportName, continent, country, city = (
                destination.airportId,
                destination.airportName,
                destination.continent,
                destination.country,
                destination.city,
            )
        elif {"airportId", "airportName", "continent", "country", "city"} <= kwargs.keys():
            airportId = kwargs["airportId"]
            airportName = kwargs["airportName"]
            continent = kwargs["continent"]
            country = kwargs["country"]
            city = kwargs["city"]
        else:
            raise ValueError("Must provide a Destination object or airportId, airportName, continent, country, city as kwargs")

        with self.connect() as (db, cursor):
            try:
                cursor.execute(
                    "INSERT INTO destinations (airportId, airportName, continent, country, city) VALUES (?, ?, ?, ?, ?)",
                    (airportId, airportName, continent, country, city),
                )
            except Exception as e:
                db.rollback()
                raise e

    def update(self, airportId: str, **kwargs: object) -> None:
        allowed_fields = {"airportName", "continent", "country", "city"}
        set_clauses = []
        values = []

        for field, value in kwargs.items():
            if field in allowed_fields:
                set_clauses.append(f"{field}=?")
                values.append(value)

        if not set_clauses:
            raise ValueError("No valid fields provided to update")

        values.append(airportId)

        with self.connect() as (db, cursor):
            cursor.execute(
                f"UPDATE destinations SET {', '.join(set_clauses)} WHERE airportId=?",
                tuple(values),
            )

    def delete(self, airportId: str) -> None:
        with self.connect() as (db, cursor):
            cursor.execute("DELETE FROM destinations WHERE airportId=?", (airportId,))