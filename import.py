import csv
import os

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))

def main():
    id=0
    review=0
    average=0
    isAble= True

    print("db value: ",db)

    f = open("books.csv")
    reader = csv.reader(f)
    for isbn, title, author, year in reader:
        db.execute("INSERT INTO books (book_id, isbn, title, author, year, isAble, review, average ) VALUES (:book_id, :isbn, :title, :author, :year, :isAble, :review, :average)",
                   {"book_id":id, "isbn":isbn, "title":title, "author":author, "year":year, "isAble":isAble, "review":review, "average":average})
        print(f"Added book | {id} | {isbn} | {title} | {author}")
        id+=1
    db.commit()

if __name__ == "__main__":
    main()
