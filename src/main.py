import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.api import users, statements, transactions, categories


# Log conf
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

app = FastAPI()

origins = [
    "http://localhost:5173",  # Front-end addr
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(users.router)
app.include_router(statements.router)
app.include_router(transactions.router)
app.include_router(categories.router)


@app.get("/")
def root():
    return {"message": "Monee Flow Backend is running 😁"}
