import json
from pydantic import BaseModel
from sqlmodel import SQLModel, Field
filename = "cars.json"


class TripInput(BaseModel):
    start: int
    end: int
    description: str


class TripOutput(TripInput):
    id: int


class CarInput(BaseModel):
    size: str
    fuel: str | None = "electric"
    doors: int
    transmission: str | None = "auto"

    # Inner class Config to show sample data in postman/fastAPI
    class Config:
        json_schema_extra = {
            "example": {
                "size": "m",
                "doors": 5,
                "transmission": "manual",
                "fuel": "hybrid"
            }
        }


class CarOutput(CarInput):
    id: int
    trips: list[TripOutput] = []


def load_db() -> list[CarOutput]:
    """ Load a List of Car objects from a JSON file"""
    with open(filename) as f:
        return [CarOutput.model_validate(obj) for obj in json.load(f)]


def save_db(cars: list[CarInput]):
    """ write/save the data in the json file"""
    with open(filename, "w") as f:
        json.dump([car.model_dump() for car in cars], f, indent=4)
