from sqlalchemy.orm import Session
from src.core.config import get_db
from fastapi import Depends


class AppContext:
    def __init__(self, db: Session):
        self.db = db
        # self.queue = queue
        # self.cache = cache

def get_context(db: Session = Depends(get_db)) -> AppContext:
    return AppContext(db)
