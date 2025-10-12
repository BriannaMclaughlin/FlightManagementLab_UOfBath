import contextlib
import sqlite3
from http import HTTPStatus

from FlightManagementLab_UOfBath.Entities.Destination import Destination
from .Repository import Repository


class DestinationRepository(Repository[Destination]):
    def __init__(self, db_path: str) -> None:
        self.db_path = db_path
        self.create_table()
        self.insert_dummy_data()

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
                    country TEXT,
                    city TEXT
                )
            """)

    def insert_dummy_data(self) -> None:
        dummy_data = [
            ("LHR", "London Heathrow", "United Kingdom", "London"),
            ("LGW", "London Gatwick", "United Kingdom", "London"),
            ("STN", "London Stansted", "United Kingdom", "London"),
            ("CDG", "Charles de Gaulle", "France", "Paris"),
            ("JFK", "John F. Kennedy International", "United States", "New York"),
            ("LAX", "Los Angeles International", "United States", "Los Angeles"),
            ("DXB", "Dubai International", "United Arab Emirates", "Dubai"),
            ("HND", "Tokyo Haneda", "Japan", "Tokyo"),
            ("SIN", "Singapore Changi", "Singapore", "Singapore"),
            ("SYD", "Sydney Kingsford Smith", "Australia", "Sydney"),
        ]

        with self.connect() as (db, cursor):
            cursor.executemany("""
                INSERT OR IGNORE INTO destinations 
                (airportId, airportName, country, city)
                VALUES (?, ?, ?, ?)
            """, dummy_data)
            print(f"✅ Inserted {cursor.rowcount} new destinations (existing ones ignored).")

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

    def find_by_city(self, city: str) -> list[Destination]:
        with self.connect() as (db, cursor):
            cursor.execute("SELECT * FROM destinations WHERE city=?", (city,))
            return [Destination(*row) for row in cursor.fetchall()]

    def find_by_country(self, country: str) -> list[Destination]:
        with self.connect() as (db, cursor):
            cursor.execute("SELECT * FROM destinations WHERE country=?", (country,))

    def add(self, destination: Destination | None = None, **kwargs: object) -> None:
        if destination:
            airportId, airportName, country, city = (
                destination.airportId,
                destination.airportName,
                destination.country,
                destination.city,
            )
        elif {"airportId", "airportName", "country", "city"} <= kwargs.keys():
            airportId = kwargs["airportId"]
            airportName = kwargs["airportName"]
            country = kwargs["country"]
            city = kwargs["city"]
        else:
            raise ValueError("Must provide a Destination object or airportId, airportName, country, city as kwargs")

        with self.connect() as (db, cursor):
            try:
                cursor.execute(
                    "INSERT INTO destinations (airportId, airportName, country, city) VALUES (?, ?, ?, ?, ?)",
                    (airportId, airportName, country, city),
                )
            except Exception as e:
                db.rollback()
                print(f"insert failed: {e}")
                raise e

    def update(self, airportId: str, **kwargs: object) -> None:
        allowed_fields = {"airportName", "country", "city"}
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