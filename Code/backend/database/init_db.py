import os

from .db import engine

from .models import Base


def init_database():

    # create storage folder
    os.makedirs(
        "storage",
        exist_ok=True
    )

    # create tables
    Base.metadata.create_all(
        bind=engine
    )

    print("Database initialized.")