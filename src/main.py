import logging
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.api import users, statements, transactions, categories, summary


# Log conf
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

app = FastAPI()

allowed_origins = os.getenv("ALLOWED_ORIGINS", "http://localhost:5173").split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(users.router)
app.include_router(statements.router)
app.include_router(transactions.router)
app.include_router(categories.router)
app.include_router(summary.router)


@app.get("/")
def root():
    return {"message": "Monee Flow Backend is running 😁"}
