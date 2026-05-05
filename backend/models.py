import secrets
from werkzeug.security import generate_password_hash, check_password_hash
from backend import db

book_shelves = db.Table('book_shelves',
    db.Column('book_id',  db.Integer, db.ForeignKey('book.id',  ondelete='CASCADE'), primary_key=True),
    db.Column('shelf_id', db.Integer, db.ForeignKey('shelf.id', ondelete='CASCADE'), primary_key=True)
)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    token = db.Column(db.String(64), unique=True)
    books = db.relationship('Book', backref='owner', lazy=True)
    shelves = db.relationship('Shelf', backref='owner', lazy=True, cascade='all, delete-orphan')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def new_token(self):
        self.token = secrets.token_hex(32)
        return self.token


class Book(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    format = db.Column(db.String(10), nullable=False)
    filename = db.Column(db.String(200), nullable=False)
    cover_filename = db.Column(db.String(200), nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    current_position = db.Column(db.String(500), default='')
    current_page = db.Column(db.Integer, default=1)


class Shelf(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    books = db.relationship('Book', secondary=book_shelves, lazy=True,
                            backref=db.backref('shelves', lazy=True))
