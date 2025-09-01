import pandas as pd
import os
from src.services.parsers.factory import get_parser
from src.core.app_context import AppContext, get_context
from fastapi import FastAPI, Depends

app = FastAPI()


@app.get("/")
def root():
    return {"message": "Monee Flow Backend is running 😁"}


@app.get("/test_parser")
def qw_test_parser(ctx: AppContext = Depends(get_context)):

    user_id = '804659e9-6351-4723-b829-19a20f210bc6'

    # TD
    # column_names = ["Date", "Transaction Description", "Debit", "Credit", "Balance"]
    #
    # BASE_DIR = os.path.dirname(__file__)  # src 目录
    # file_path = os.path.join(BASE_DIR, "tmp_data", "transactions_td_chequing.csv")
    # df = pd.read_csv(file_path, names=column_names, dtype=str, header=None)
    #
    # raw_data = df.to_dict(orient='records')
    #
    # parser = get_parser('TD')
    # transactions = parser.parse(user_id, raw_data, ctx)

    # Rogers
    BASE_DIR = os.path.dirname(__file__)  # src 目录
    file_path = os.path.join(BASE_DIR, "tmp_data", "transactions_rogers.csv")
    df = pd.read_csv(file_path, dtype=str)
    raw_data = df.to_dict(orient='records')

    parser = get_parser('Rogers')
    transactions = parser.parse(user_id, raw_data, ctx)

    return transactions