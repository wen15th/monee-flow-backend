"""
Seed initial system categories.
Usage: python -m scripts.seed_system_categories
"""

from src.core.db import SessionLocal
from src.models.system_category import SystemCategory

SYSTEM_CATEGORIES = [
    "🏠 Housing",
    "🔌 Utilities",
    "🛒 Groceries & Supermarket",
    "🍔 Food & Dining",
    "🚗 Transportation",
    "🛍️ Shopping",
    "🐶 Pets",
    "💊 Health & Medical",
    "🏋️ Fitness",
    "📦 Subscription & Membership",
    "🎮 Entertainment",
    "❓ Other",
]


def seed():
    db = SessionLocal()
    try:
        existing = db.query(SystemCategory).count()
        if existing > 0:
            print(f"Skipped: {existing} system categories already exist.")
            return

        db.bulk_save_objects([SystemCategory(name=name) for name in SYSTEM_CATEGORIES])
        db.commit()
        print(f"Inserted {len(SYSTEM_CATEGORIES)} system categories.")
    finally:
        db.close()


if __name__ == "__main__":
    seed()
