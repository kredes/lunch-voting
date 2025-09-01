"""
Initializes the database and creates all tables.
"""
import pathlib
import sys

PROJECT_ROOT = pathlib.Path(__file__).parent.parent / "src/app"
sys.path.append(str(PROJECT_ROOT))

from app.db import DatabaseModel
from app.db.connections import get_engine

if __name__ == "__main__":
    DatabaseModel.metadata.create_all(get_engine(), checkfirst=True)
