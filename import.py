import csv
import os

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

from time import time

# Check for environment variable
if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")

engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))

def main():

    # creates the table
    create_table = """CREATE TABLE locations (
	zipcode VARCHAR NOT NULL UNIQUE,
	city VARCHAR NOT NULL,
	state VARCHAR NOT NULL,
	latitude DECIMAL NOT NULL,
	longitude DECIMAL NOT NULL,
	population INTEGER NOT NULL
);"""

    db.execute(create_table)

    # Open a file using Python's CSV reader.
    f = open("zips.csv")
    reader = csv.reader(f)

    # Iterate over the rows of the opened CSV file.
    for i, (zipcode, city, state, latitude, longitude, population) in enumerate(reader):
        if i != 0:

            values = {
                "z": zipcode.zfill(5),
                "c": city,
                "s": state,
                "a": latitude,
                "o": longitude,
                "p": population
            }

            add_row = """INSERT INTO locations
            (zipcode, city, state, latitude, longitude, population)
            VALUES (:z, :c, :s, :a, :o, :p)"""

            db.execute(add_row, values)

            print(f"added row {i}")

    db.commit()

if __name__ == "__main__":
    main()
