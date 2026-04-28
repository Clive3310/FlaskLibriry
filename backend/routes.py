from flask import jsonify, request
from app.backend import app, db
from app.backend.models import User, Book


# Регистрация пользователя
@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    new_user = User(username=data['username'], password=data['password'])
    db.session.add(new_user)
    db.session.commit()
    return jsonify({'message': 'User created'}), 201


# Авторизация
@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    user = User.query.filter_by(username=data['username']).first()
    if user and user.password == data['password']:
        return jsonify({'message': 'Login successful'}), 200
    return jsonify({'message': 'Invalid credentials'}), 401


# Загрузка книги
@app.route('/books', methods=['POST'])
def upload_book():
    file = request.files['file']
    book = Book(
        title=file.filename,
        format=file.filename.split('.')[-1],
        path=f'uploads/{file.filename}',
        user_id=request.json['user_id']
    )
    file.save(book.path)
    db.session.add(book)
    db.session.commit()
    return jsonify({'message': 'Book uploaded'}), 201


# Получение списка книг
@app.route('/books', methods=['GET'])
def get_books():
    books = Book.query.all()
    return jsonify([{'id': b.id, 'title': b.title} for b in books])