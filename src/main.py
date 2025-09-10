import logging
from fastapi import FastAPI
from src.api import users, statements, transactions, categories


# Log conf
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

app = FastAPI()


app.include_router(users.router)
app.include_router(statements.router)
app.include_router(transactions.router)
app.include_router(categories.router)


@app.get("/")
def root():
    return {"message": "Monee Flow Backend is running 😁"}
