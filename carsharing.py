import uvicorn
from fastapi import FastAPI, HTTPException, Depends
from sqlmodel import create_engine, SQLModel, Session, select

from scehemas import CarInput, CarOutput, TripOutput, TripInput, Car, Trip

app = FastAPI(title="Car Sharing")


engine = create_engine(
    "sqlite:///carsharing.db",
    connect_args={"check_same_thread": False},  # Needed for SQLite
    echo=True  # Log generated SQL
)


@app.on_event("startup")
def on_startup():
    SQLModel.metadata.create_all(engine)


def get_session():
    """ return a session object | dependency injection"""
    with Session(engine) as session:
        yield session



@app.get("/api/cars")
def get_cars(size: str | None = None, doors: int | None = None,
             session: Session = Depends(get_session)) -> list:
    """ this optional params only works for 3.10
        for 3.10 lower use
        get_cars(size: Optional[str] = None, doors: Optional[str] = None) -> List:
        and don't forget to import Optional
    """
    """ return all cars"""
    '''
    return [car for car in db if car['size] == size]
    '''

    query = select(Car)
    if size:
        query = query.where(Car.size == size)
    if doors:
        query = query.where(Car.doors >= doors)
    return session.exec(query).all()


@app.get("/api/cars/{id}", response_model=CarOutput)
def car_by_id(id: int,  session: Session = Depends(get_session)) -> CarOutput:
    """ Return a Car Object"""
    car = session.get(Car, id)
    if car:
        return car
    else:
        raise HTTPException(status_code=404, detail=f"No car with id= {id}")


@app.post("/api/cars", response_model=Car)
def add_car(car_input: CarInput,  session: Session = Depends(get_session)) -> Car:
    """ add a new car object"""
    new_car = Car.from_orm(car_input)
    session.add(new_car)
    session.commit()
    session.refresh(new_car)
    return new_car


@app.post("/api/cars/{car_id}/trips", response_model=Trip)
def add_trip(car_id: int, trip_input: TripInput,
             session : Session = Depends(get_session)) -> Trip:
    """ add trips to an existing car"""
    car = session.get(Car, car_id)
    if car:
        new_trip = Trip.from_orm(trip_input, update={'car_id' : car_id})
        car.trips.append(new_trip)
        session.commit()
        session.refresh(new_trip)
        return new_trip
    else:
        raise HTTPException(status_code=404, detail=f"No car with id={id}")


@app.delete("/api/cars/{id}", status_code=204)
def remove_car(id: int,  session: Session = Depends(get_session)) -> None:
    """ remove/delete a car"""
    car = session.get(Car, id)
    if car:
        session.delete(car)
        session.commit()
    else:
        raise HTTPException(status_code=404, detail=f"No car with id={id}.")


@app.put("/api/cars/{id}", response_model=Car)
def change_car(id: int, new_data: CarInput, session: Session = Depends(get_session)) -> Car:
    """ Updates an existing car"""
    car = session.get(Car, id)
    if car:
        car.fuel = new_data.fuel
        car.transmission = new_data.transmission
        car.size = new_data.size
        car.doors = new_data.doors
        session.commit()
        return car
    else:
        raise HTTPException(status_code=404, detail=f"No car with id={id}")


""" To run the server : in the terminal run uvicorn carsharing:app --reload"""

if __name__ == "__main__":
    uvicorn.run("carsharing:app", reload=True)
