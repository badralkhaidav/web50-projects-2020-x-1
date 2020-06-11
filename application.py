from flask import Flask, session, render_template, request, jsonify, json
import requests
from adduser import *
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import  scoped_session, sessionmaker

app = Flask(__name__)

# Set up database
engine = create_engine("postgres://vfemefkkfvpndz:7dda029ddaa79d315de1313328e07ab73277d64e97b5b8e7da7a5b787529f04d@ec2-54-247-103-43.eu-west-1.compute.amazonaws.com:5432/d8qr7lndoqe6lh")
db = scoped_session(sessionmaker(bind=engine))


@app.route("/")
def index():

    return render_template("index.html")

@app.route("/login", methods=["POST"])
def login():
    username=request.form.get("login_name")
    passwrd=request.form.get("password")
    count=0
    count = int(db.execute("SELECT * FROM user_test WHERE login_name=:login_name and password=:password",{"login_name":username , "password":passwrd}).rowcount)
    global user_idd
    user_idd = db.execute("SELECT user_id FROM user_test WHERE login_name=:login_name and password=:password",{"login_name":username , "password":passwrd}).fetchone()[0]
    if user_idd == -1 :
        return render_template("index.html", message="User name or password incorrect!")
    else:

        return render_template("search.html", message=user_idd)


@app.route("/books", methods=["POST"])
def books():
    isbn=request.form.get("isbn")
    title=request.form.get("title")
    author=request.form.get("author")
    count_book =int(db.execute("SELECT * FROM books WHERE isbn=:isbn or author=:author or title=:title",{"isbn":isbn, "author":author, "title":title}).rowcount)

    if  count_book== 0:
        return render_template("error.html", message = "book not found")

    books = db.execute("SELECT * FROM books WHERE isbn=:isbn or author=:author or title=:title",{"isbn":isbn, "author":author, "title":title}).fetchall()

    return render_template("books.html", books=books)


@app.route("/books/<int:book_id>")
def book(book_id):
    #book = db.execute("SELECT * FROM books WHERE book_id = :id", {"id": 1}).fetchone()
    book = db.execute("SELECT * FROM books WHERE book_id = :id", {"id": book_id}).fetchone()

    if book is None:
        return render_template("error.html", message="book not found")
    reviews = db.execute("SELECT * FROM books_review WHERE book_id = :book_id",
                            {"book_id": book_id}).fetchall()

    #res = requests.get("https://www.goodreads.com/book/review_counts.json", params={"key": "zH77FX6pcD1Q9XdUT2u1fA", "isbns": "380795272"})
    res = requests.get("https://www.goodreads.com/book/review_counts.json", params={"key": "zH77FX6pcD1Q9XdUT2u1fA", "isbns": "1439102724"})

    if res.status_code != 200:
      return render_template("error.html", message="book not found in goodread")
    reviews_count=res.json()["books"][0]["reviews_count"]
    #reviews_count = res.json()["books"][0]["reviews_count"]
    return render_template("book.html", book=book, reviews=reviews, reviews_count=reviews_count)

@app.route("/api/<string:isbn>")
def api(isbn):
    book = db.execute("SELECT * FROM books WHERE isbn = :isbn", {"isbn": isbn}).fetchone()
    return jsonify({
        "author": book.author,
        "title": book.title,
        "year": book.year,
        "isbn": book.isbn,
        "review_count": book.review,
        "average_score": book.average
    })

@app.route("/register")
def register():
    return render_template("register.html")

@app.route("/registered", methods=["POST"])
def registered():
    reg_username=request.form.get("login_name")
    reg_passwrd=request.form.get("password")

    max_id=db.execute("SELECT MAX(user_id) FROM user_test ").fetchone()[0]
    max_id+=1

    db.execute("INSERT INTO user_test (user_id, login_name, password) VALUES (:user_id,:login_name, :password)",{"user_id":max_id,"login_name":reg_username, "password":reg_passwrd})
    db.commit()

    return render_template("index.html")

@app.route("/books/<int:book_id>/review", methods=["POST"])
def review(book_id):
    rate=int(request.form.get("rates"))
    review=request.form.get("review")

    user_review=db.execute("SELECT user_id FROM books_review WHERE user_id=:user_id and book_id=:book_id",{"user_id":user_idd, "book_id":book_id}).rowcount

    if user_review > 0:
        return render_template("error.html", message="Thanks,you have alreadt submitted your review for this book. ")
    max_id1= db.execute("SELECT MAX(id) FROM books_review ").fetchone()[0]
    if max_id1 is None:
        max_id1=0
    max_id1+=1

    review_average_review=db.execute("SELECT average, review FROM books WHERE book_id = :id", {"id": book_id}).fetchone()
    review_average=float(review_average_review[0])
    review_amount=int(review_average_review[1])

    review_average= (review_average*review_amount+rate)/(review_amount+1)

    review_amount+=1

    db.execute("INSERT INTO books_review (id, rate, review, book_id, user_id) VALUES (:id,:rate, :review, :book_id, :user_id)",{"id":max_id1,"rate":rate, "review":review, "book_id":book_id, "user_id":user_idd})
    db.execute("UPDATE books SET average=:average , review=:review WHERE book_id=:book_id",{"average":review_average,"review":review_amount,"book_id":book_id})


    db.commit()

    return render_template("search.html", message="Review submitted")
