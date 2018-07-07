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


    command = """CREATE TABLE locations (
	zipcode INTEGER PRIMARY KEY,
	city VARCHAR NOT NULL,
	state CHAR(2) NOT NULL,
	latitude DECIMAL NOT NULL,
	longitude DECIMAL NOT NULL,
	population INTEGER NOT NULL
);"""

    db.execute(command)

    # Open a file using Python's CSV reader.
    f = open("zips.csv")
    reader = csv.reader(f)

    # Iterate over the rows of the opened CSV file.
    for i, data in enumerate(reader):
        if i != 0:
            # t = time()
            variables = {"z": data[0], "c": data[1], "s": data[2], "a": data[3], "o": data[4], "p": data[5]}
            db.execute("INSERT INTO locations (zipcode, city, state, latitude, longitude, population) VALUES (:z, :c, :s, :a, :o, :p)",
                    variables)
            # t = time() - t
            print(f"did it {i}")
    db.commit()

if __name__ == "__main__":
    main()
