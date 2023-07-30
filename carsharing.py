import uvicorn
from fastapi import FastAPI, Request
from sqlmodel import SQLModel
from starlette.middleware.cors import CORSMiddleware
from starlette.responses import JSONResponse
from starlette.status import HTTP_422_UNPROCESSABLE_ENTITY

from db import engine
from routers import cars, web
from routers.cars import BadTripException

app = FastAPI(title="Car Sharing")
app.include_router(cars.router)
app.include_router(web.router)


origins = [
    "http://localhost:8000",
    "http://localhost:8080"
]


app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)


@app.on_event("startup")
def on_startup():
    SQLModel.metadata.create_all(engine)


@app.exception_handler(BadTripException)
async def unicorn_exception_handler(request: Request, exc: BadTripException):
    return JSONResponse(
        status_code=HTTP_422_UNPROCESSABLE_ENTITY,
        content={"message": "Bad Trip"}
    )


@app.middleware("http")
async def add_cars_cookie(request: Request, call_next):
    # middleware that add cookies
    response = await call_next(request)
    response.set_cookie(key="cars_cookie", value="you_visited_the_carsharing_app")
    return response


""" To run the server : in the terminal run uvicorn carsharing:app --reload"""
if __name__ == "__main__":
    uvicorn.run("carsharing:app", reload=True)
