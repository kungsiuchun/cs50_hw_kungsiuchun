import os
import requests

from flask import Flask, session, render_template, request, redirect, url_for, flash, jsonify
from flask_session import Session
from sqlalchemy import create_engine, or_
from sqlalchemy.orm import scoped_session, sessionmaker
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask_wtf import FlaskForm 
from wtforms import StringField, PasswordField, BooleanField
from wtforms.validators import InputRequired, Email, Length
from flask_sqlalchemy  import SQLAlchemy
from models import *

app = Flask(__name__)
api_key ="Y65zIp8A2aIhm7q5wPStWA"

# Check for environment variable
if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")

# res = requests.get("https://www.goodreads.com/book/review_counts.json", params={"key": api_key, "isbns": "9781632168146"})
# print(res.json())

# $env:DATABASE_URL ="postgres://ffgfceuxuebxmt:7685e6e30fd272c08db27e80fa31ef5fcbf3f226ddd7c570122fbba1a8175ade@ec2-54-86-170-8.compute-1.amazonaws.com:5432/d35d8pie09cjqv"
# Configure session to use filesystem
# app.config["SESSION_PERMANENT"] = False
# app.config["SESSION_TYPE"] = "filesystem"
app.config['SECRET_KEY'] = 'Thisissupposedtobesecret!'
login_manager = LoginManager(app)
# login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message_category = 'info'
# Session(app)

# Set up database
# engine = create_engine(os.getenv("DATABASE_URL"))
# db = scoped_session(sessionmaker(bind=engine))
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv("DATABASE_URL") 
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route("/")
@app.route("/home")
def index():
    # books = db.execute("SELECT isbn, title, author, year from books LIMIT 10").fetchall()
    page = request.args.get('page', 1, type=int)
    # posts = Post.query.order_by(Post.date_posted.desc()).paginate(page=page, per_page=5)
    books = Book.query.order_by(Book.title.asc()).paginate(page=page, per_page=9)
    print(books)
    return render_template("index.html", books=books)

@app.route("/book/<string:id>")
def book(id):
    # book = db.execute("SELECT * FROM books WHERE isbn = :id ",{"id": id}).fetchone()
    book = Book.query.get(id)
    print(book.isbn)

    rev = Review.query.filter(Review.isbn==book.isbn).all()
    # rev = db.session.query(Review).all()
    # rev = Review.select().limit(5)
    res = requests.get(
        "https://www.goodreads.com/book/review_counts.json",
        params={
            "key": api_key,
            "isbns": id})
    if res.status_code != 200:
        raise Exception("ERROR: API request unsuccessful")
    else:
        data = res.json()
        review = data["books"][0]["work_reviews_count"]
        rate = data["books"][0]["average_rating"]

    

    return render_template("book.html", book=book, reviews=rev, review=review, rate=rate)

@app.route("/login", methods=['POST', 'GET'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()

    if form.validate_on_submit():
        # user = db.execute("SELECT * FROM users WHERE name = :name", 
        # {"name": form.username.data}).fetchone()
        user = User.query.filter_by(name=form.username.data).first()
        if user:
            if check_password_hash(user.password, form.password.data):
                login_user(user, remember=form.remember.data)
                return render_template("dashboard.html", name=form.username.data)
        
        flash('Login Unsuccessful. Please check email and password', 'danger')
        return render_template("login.html", form=form, mes="Invalid login")

    # return redirect(url_for('login'), mes="hi")
    return render_template("login.html", form=form)


@app.route("/register")
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegisterForm()
    return render_template("register.html", form=form)
    
@app.route("/newUser", methods=["POST"])
def newUser():
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    form = RegisterForm()

    if form.validate_on_submit():
        hashed_password = generate_password_hash(form.password.data, method='sha256')
        # name = form.username.data
        # x = db.execute("SELECT * FROM users WHERE name = :name", {"name": form.username.data}).rowcount
        # if x > 0:
        #     return render_template("register.html", mes="The username is already taken")  
        # db.execute("INSERT INTO users (name, password) VALUES (:name, :password)", {"name": name, "password": hashed_password})
        
        new_user = User(name=form.username.data, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        flash('Successful registered', 'success')
        return redirect(url_for('index'))
        
    return render_template("index.html", mes="Invalid input")

@app.route("/search", methods=['POST'])
def search():
    search = request.form.get("type", None)
    query = request.form.get("query", None)
    src = "%{}%".format(query)

    q = Book.query.filter(or_(Book.author.like(src),
    Book.title.like(src),
    Book.author.like(src)))

    if search == "isbn":
        q = Book.query.filter(Book.isbn.like(src)).all()
    if search == "title":
        q = Book.query.filter(Book.title.like(src)).all()
    if search == "author":
        q = Book.query.filter(Book.author.like(src)).all()
    
    return render_template("search.html", books=q)

@app.route("/review/<string:id>", methods=['POST'])
@login_required
def review(id):
    star = int(request.form.get("star", None))
    rev = request.form.get("review", None)

    review = Review(isbn=id, content=rev, star=star, author=current_user)
    db.session.add(review)
    db.session.commit()
    flash('Your review has been created!', 'success')
    return redirect(url_for('book', id=id)) 

@app.route("/api/<string:isbn>")
def book_api(isbn):

    book = Book.query.get(isbn)
    if book is None:
        return jsonify({"error": "Invalid isbn"}), 422
    
    review_count = Review.query.filter(Review.isbn==isbn).count()
    book_review = Review.query.filter(Review.isbn==isbn).all()
    total_score = 0
    average_score = 0
    for i in book_review:
        total_score += i.star
    if review_count == 0:
        average_score = 0
    else:
        average_score = total_score / review_count

    return jsonify({
        "title": book.title,
        "author": book.author,
        "year": book.year,
        "isbn": book.isbn,
        "review_count": review_count,
        "average_score": average_score
    })


@app.route("/logout")
def logout():
    logout_user()
    flash("You have been log out!","success")
    return redirect(url_for('index'))




@app.route("/dashboard")
def dashboard():
    
    current_id = current_user.get_id()
    name = User.query.get(current_id)
    rev = Review.query.filter(Review.user_id==current_id).all()

    
    return render_template("dashboard.html", name= name.name, reviews=rev)



   
class LoginForm(FlaskForm):
    username = StringField('username', validators=[InputRequired(), Length(min=4, max=15)])
    password = PasswordField('password', validators=[InputRequired(), Length(min=4, max=80)])
    remember = BooleanField('remember me')

class RegisterForm(FlaskForm):
    username = StringField('username', validators=[InputRequired(), Length(min=4, max=15)])
    password = PasswordField('password', validators=[InputRequired(), Length(min=4, max=80)])

