import csv
import os

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))

def main():

    db.execute("ALTER TABLE books_review ADD book_id int")

    #db.execute("CREATE TABLE books_review (id int PRIMARY KEY UNIQUE, rate int, review varchar, data timestamp, isAble boolean DEFAULT true, user_id int )")

    #db.execute("CREATE TABLE books (book_id int PRIMARY KEY UNIQUE, isbn varchar, title varchar, author varchar, year int, isAble boolean, review int, average float)")
    db.commit()



if __name__ == "__main__":
    main()
