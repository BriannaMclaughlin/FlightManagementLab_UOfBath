import contextlib
import sqlite3

from .Repository import Repository
from ..Entities.Pilot import Pilot


class PilotRepository(Repository[Pilot]):
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

    def create_table(self) -> None:
        with self.connect() as (db, cursor):
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS pilots (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    first_name TEXT NOT NULL,
                    last_name TEXT NOT NULL,
                    license_number VARCHAR NOT NULL UNIQUE,
                    rank TEXT NOT NULL,
                    experience_hours INTEGER NOT NULL,
                    home_airport TEXT NOT NULL,
                    active INTEGER NOT NULL CHECK (active IN (0, 1))
                )
            """)

    def insert_dummy_data(self) -> None:
        dummy_pilots = [
            ("John", "Sanderson", "LIC001", "Captain", 12000, "LHR", 1),
            ("Emma", "Foster", "LIC002", "First Officer", 4500, "JFK", 1),
            ("Liam", "Nguyen", "LIC003", "Captain", 9800, "DXB", 1),
            ("Sophia", "Chen", "LIC004", "First Officer", 3200, "SIN", 0),
            ("Michael", "Brown", "LIC005", "Captain", 15000, "CDG", 1),
            ("Olivia", "Garcia", "LIC006", "First Officer", 6000, "LAX", 1),
            ("Noah", "Kumar", "LIC007", "Captain", 11000, "STN", 1),
            ("Ava", "Petrov", "LIC008", "First Officer", 2500, "ORD", 0),
            ("Ethan", "Hughes", "LIC009", "Captain", 13000, "LHR", 1),
            ("Isabella", "Miller", "LIC010", "First Officer", 7000, "JFK", 1)
        ]

        with self.connect() as (db, cursor):
            cursor.executemany("""
                INSERT OR IGNORE INTO pilots
                (first_name, last_name, license_number, rank, experience_hours, home_airport, active)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, dummy_pilots)
            print(f"✅ Inserted {cursor.rowcount} new pilots (existing ones ignored).")

    def get(self, id: int) -> Pilot:
        with self.connect() as (db, cursor):
            cursor.execute("SELECT * FROM pilots WHERE id=?", (id,))
            row = cursor.fetchone()
            if row is None:
                raise ValueError(f"Pilot with id {id} does not exist")
            return Pilot(
                id=row["id"],
                first_name=row["first_name"],
                last_name=row["last_name"],
                license_number=row["license_number"],
                rank=row["rank"],
                experience_hours=row["experience_hours"],
                home_airport=row["home_airport"],
                active=row["active"]
            )

    def get_all(self) -> list[Pilot]:
        with self.connect() as (db, cursor):
            cursor.execute("SELECT * FROM pilots")
            return [Pilot(
                id=row["id"],
                first_name=row["first_name"],
                last_name=row["last_name"],
                license_number=row["license_number"],
                rank=row["rank"],
                experience_hours=row["experience_hours"],
                home_airport=row["home_airport"],
                active=row["active"]
            ) for row in cursor.fetchall()]

    def add(self, pilot: Pilot | None = None, **kwargs: object) -> None:
        if pilot:
            (first_name, last_name, license_number, rank, experience_hours, home_airport, active) = (
                pilot.first_name,
                pilot.last_name,
                pilot.license_number,
                pilot.rank,
                pilot.experience_hours,
                pilot.home_airport,
                pilot.active
            )
        elif {"first_name", "last_name", "license_number", "rank",
              "experience_hours", "home_airport", "active"} <= kwargs.keys():
            first_name = kwargs["first_name"]
            last_name = kwargs["last_name"]
            license_number = kwargs["license_number"]
            rank = kwargs["rank"]
            experience_hours = kwargs["experience_hours"]
            home_airport = kwargs["home_airport"]
            active = kwargs["active"]
        else:
            raise ValueError("Must provide a Pilot object or first_name, last_name, license_number,"
                             "rank, experience_hours and home_airport as kwargs")

        with self.connect() as (db, cursor):
            try:
                cursor.execute(
                    "INSERT INTO pilots (first_name, last_name, license_number, rank, "
                    "experience_hours, home_airport, active) VALUES (?, ?, ?, ?, ?, ?, ?)",
                    (first_name, last_name, license_number, rank, experience_hours, home_airport, active),
                )
            except Exception as e:
                db.rollback()
                raise e

    def update(self, pilot_id: int, **kwargs: object) -> None:
        allowed_fields = {"first_name", "last_name", "license_number", "rank", "experience_hours", "home_airport", "active"}

        set_clauses = []
        values = []

        for field, value in kwargs.items():
            if field in allowed_fields:
                set_clauses.append(f"{field}=?")
                values.append(value)

        if not set_clauses:
            raise ValueError("No valid fields provided to update")

        values.append(pilot_id)

        with self.connect() as (db, cursor):
            cursor.execute(
                f"UPDATE pilots SET {', '.join(set_clauses)} WHERE id=?",
                tuple(values),
            )

    def delete(self, pilot_id: int) -> None:
        with self.connect() as (db, cursor):
            cursor.execute("DELETE FROM pilots WHERE id=?", (pilot_id,))

    def find_by_last_name(self, last_name: str) -> list[Pilot]:
        with self.connect() as (db, cursor):
            cursor.execute("SELECT * FROM pilots WHERE last_name=?", (last_name,))
            rows = cursor.fetchall()
            return [
                Pilot(
                    id=row["id"],
                    first_name=row["first_name"],
                    last_name=row["last_name"],
                    license_number=row["license_number"],
                    rank=row["rank"],
                    experience_hours=row["experience_hours"],
                    home_airport=row["home_airport"],
                    active=bool(row["active"])
                )
                for row in rows
            ]