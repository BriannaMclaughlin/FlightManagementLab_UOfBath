import contextlib
import sqlite3

from .Repository import Repository
from ..Entities.FlightAssignment import FlightAssignment


class FlightAssignmentRepository():
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
                CREATE TABLE IF NOT EXISTS flight_assignment (
                    flight_id INTEGER,
                    pilot_id INTEGER,
                    PRIMARY KEY (flight_id, pilot_id),
                    FOREIGN KEY (flight_id) REFERENCES flights(id),
                    FOREIGN KEY (pilot_id) REFERENCES pilots(id)
                )
            """)

    def insert_dummy_data(self) -> None:
        dummy_data = [
            #flight id, pilot id
            ("4", "1"),
            ("4", "2"),
            ("3", "3"),
            ("3", "4")
        ]
        with self.connect() as (db, cursor):
            cursor.executemany("""
                            INSERT OR IGNORE INTO flight_assignment
                            (flight_id, pilot_id)
                            VALUES (?, ?)
                        """, dummy_data)
            print(f"✅ Inserted {cursor.rowcount} new flight assignments (existing ones ignored).")


    def get_pilots_for_flight(self, flight_id: int) -> list[int]:
        with self.connect() as (db, cursor):
            cursor.execute("SELECT pilot_id FROM flight_assignment WHERE flight_id=?", (flight_id,))
            rows = cursor.fetchall()
            return [row["pilot_id"] for row in rows] if rows else []

    def get_flights_for_pilot(self, pilot_id) -> list[int]:
        with self.connect() as (db, cursor):
            cursor.execute("SELECT flight_id FROM flight_assignment WHERE pilot_id=?", (pilot_id,))
            rows = cursor.fetchall()
            return [row["flight_id"] for row in rows] if rows else []

    def assign_pilot_to_flight(self, flight_id: int, pilot_id: int) -> bool:
        with self.connect() as (db, cursor):
            cursor.execute(
                "INSERT OR IGNORE INTO flight_assignment (flight_id, pilot_id) VALUES (?, ?)",
                (flight_id, pilot_id)
            )
            return cursor.rowcount > 0

    def unassign_pilot_from_flight(self, flight_id: int, pilot_id: int) -> bool:
        with self.connect() as (db, cursor):
            cursor.execute(
                "DELETE FROM flight_assignment WHERE flight_id=? AND pilot_id=?",
                (flight_id, pilot_id)
            )
            return cursor.rowcount > 0

    def unassign_all_pilots_from_flight(self, flight_id) -> bool:
        with self.connect() as (db, cursor):
            cursor.execute(
                "DELETE FROM flight_assignment WHERE flight_id=?",
                (flight_id,)
            )
            return cursor.rowcount > 0
