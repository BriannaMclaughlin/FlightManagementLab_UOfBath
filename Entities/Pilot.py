from dataclasses import dataclass
import datetime

@dataclass
class Pilot:
    id: int  #Primary Key
    name: str
    licenseNumber: str
    rank: str
    experienceYears: int
    