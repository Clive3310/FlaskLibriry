import os
import uuid
from flask import jsonify, request, send_from_directory
from werkzeug.utils import secure_filename
from backend import app, db
from backend.models import User, Book, Shelf

ALLOWED_BOOKS  = {'epub', 'fb2', 'png', 'jpg', 'jpeg', 'gif', 'webp', 'pdf'}
ALLOWED_COVERS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}


def current_user():
    token = request.headers.get('Authorization', '').replace('Bearer ', '').strip()
    if not token:
        return None
    return db.session.execute(db.select(User).filter_by(token=token)).scalar_one_or_none()


def covers_dir():
    d = os.path.join(app.config['UPLOAD_FOLDER'], 'covers')
    os.makedirs(d, exist_ok=True)
    return d


# ── Auth ──────────────────────────────────────────────────────────────────────

@app.route('/api/register', methods=['POST'])
def register():
    data = request.get_json() or {}
    username = data.get('username', '').strip()
    password = data.get('password', '')
    if not username or not password:
        return jsonify({'error': 'Укажите имя пользователя и пароль'}), 400
    if db.session.execute(db.select(User).filter_by(username=username)).scalar_one_or_none():
        return jsonify({'error': 'Пользователь уже существует'}), 409
    user = User(username=username)
    user.set_password(password)
    db.session.add(user)
    db.session.commit()
    return jsonify({'message': 'Пользователь создан'}), 201


@app.route('/api/login', methods=['POST'])
def login():
    data = request.get_json() or {}
    user = db.session.execute(
        db.select(User).filter_by(username=data.get('username', ''))
    ).scalar_one_or_none()
    if user and user.check_password(data.get('password', '')):
        token = user.new_token()
        db.session.commit()
        return jsonify({'token': token, 'user_id': user.id, 'username': user.username})
    return jsonify({'error': 'Неверные данные'}), 401


# ── Books ─────────────────────────────────────────────────────────────────────

@app.route('/api/books', methods=['GET'])
def get_books():
    books = db.session.execute(db.select(Book)).scalars().all()
    return jsonify([{
        'id': b.id,
        'title': b.title,
        'format': b.format,
        'user_id': b.user_id,
        'has_cover': bool(b.cover_filename),
    } for b in books])


@app.route('/api/books', methods=['POST'])
def upload_book():
    user = current_user()
    if not user:
        return jsonify({'error': 'Необходима авторизация'}), 401
    if 'file' not in request.files:
        return jsonify({'error': 'Файл не найден'}), 400
    file = request.files['file']
    if not file.filename:
        return jsonify({'error': 'Пустое имя файла'}), 400
    ext = file.filename.rsplit('.', 1)[-1].lower() if '.' in file.filename else ''
    if ext not in ALLOWED_BOOKS:
        return jsonify({'error': f'Формат .{ext} не поддерживается'}), 400
    safe = secure_filename(file.filename)
    unique_name = f"{uuid.uuid4().hex}_{safe}"
    file.save(os.path.join(app.config['UPLOAD_FOLDER'], unique_name))

    book = Book(title=file.filename.rsplit('.', 1)[0], format=ext,
                filename=unique_name, user_id=user.id)
    db.session.add(book)
    db.session.commit()
    return jsonify({'id': book.id, 'title': book.title}), 201


@app.route('/api/books/<int:book_id>/file')
def get_book_file(book_id):
    book = db.get_or_404(Book, book_id)
    return send_from_directory(app.config['UPLOAD_FOLDER'], book.filename)


@app.route('/api/books/<int:book_id>/position', methods=['GET'])
def get_position(book_id):
    book = db.get_or_404(Book, book_id)
    return jsonify({'position': book.current_position, 'page': book.current_page})


@app.route('/api/books/<int:book_id>/position', methods=['PUT'])
def save_position(book_id):
    if not current_user():
        return jsonify({'error': 'Необходима авторизация'}), 401
    book = db.get_or_404(Book, book_id)
    data = request.get_json() or {}
    book.current_position = data.get('position', '')
    book.current_page = data.get('page', 1)
    db.session.commit()
    return jsonify({'message': 'Сохранено'})


@app.route('/api/books/<int:book_id>', methods=['DELETE'])
def delete_book(book_id):
    user = current_user()
    if not user:
        return jsonify({'error': 'Необходима авторизация'}), 401
    book = db.get_or_404(Book, book_id)
    if book.user_id != user.id:
        return jsonify({'error': 'Нет доступа'}), 403
    path = os.path.join(app.config['UPLOAD_FOLDER'], book.filename)
    if os.path.exists(path):
        os.remove(path)
    if book.cover_filename:
        cp = os.path.join(covers_dir(), book.cover_filename)
        if os.path.exists(cp):
            os.remove(cp)
    db.session.delete(book)
    db.session.commit()
    return jsonify({'message': 'Удалено'})


# ── Covers ────────────────────────────────────────────────────────────────────

@app.route('/api/books/<int:book_id>/cover', methods=['POST'])
def upload_cover(book_id):
    user = current_user()
    if not user:
        return jsonify({'error': 'Необходима авторизация'}), 401
    book = db.get_or_404(Book, book_id)
    if 'cover' not in request.files:
        return jsonify({'error': 'Файл не найден'}), 400
    file = request.files['cover']
    ext = file.filename.rsplit('.', 1)[-1].lower() if '.' in file.filename else ''
    if ext not in ALLOWED_COVERS:
        return jsonify({'error': 'Допустимые форматы: PNG, JPG, GIF, WEBP'}), 400
    if book.cover_filename:
        old = os.path.join(covers_dir(), book.cover_filename)
        if os.path.exists(old):
            os.remove(old)
    name = f"{uuid.uuid4().hex}.{ext}"
    file.save(os.path.join(covers_dir(), name))
    book.cover_filename = name
    db.session.commit()
    return jsonify({'cover_url': f'/api/books/{book_id}/cover/file'})


@app.route('/api/books/<int:book_id>/cover/file')
def get_cover(book_id):
    book = db.get_or_404(Book, book_id)
    if not book.cover_filename:
        return '', 404
    return send_from_directory(covers_dir(), book.cover_filename)


# ── Shelves ───────────────────────────────────────────────────────────────────

@app.route('/api/shelves', methods=['GET'])
def get_shelves():
    user = current_user()
    if not user:
        return jsonify([])
    shelves = db.session.execute(
        db.select(Shelf).filter_by(user_id=user.id)
    ).scalars().all()
    return jsonify([{
        'id': s.id,
        'name': s.name,
        'book_ids': [b.id for b in s.books]
    } for s in shelves])


@app.route('/api/shelves', methods=['POST'])
def create_shelf():
    user = current_user()
    if not user:
        return jsonify({'error': 'Необходима авторизация'}), 401
    data = request.get_json() or {}
    name = data.get('name', '').strip()
    if not name:
        return jsonify({'error': 'Укажите название полки'}), 400
    shelf = Shelf(name=name, user_id=user.id)
    db.session.add(shelf)
    db.session.commit()
    return jsonify({'id': shelf.id, 'name': shelf.name, 'book_ids': []}), 201


@app.route('/api/shelves/<int:shelf_id>', methods=['PUT'])
def rename_shelf(shelf_id):
    user = current_user()
    if not user:
        return jsonify({'error': 'Необходима авторизация'}), 401
    shelf = db.get_or_404(Shelf, shelf_id)
    if shelf.user_id != user.id:
        return jsonify({'error': 'Нет доступа'}), 403
    data = request.get_json() or {}
    name = data.get('name', '').strip()
    if name:
        shelf.name = name
        db.session.commit()
    return jsonify({'id': shelf.id, 'name': shelf.name})


@app.route('/api/shelves/<int:shelf_id>', methods=['DELETE'])
def delete_shelf(shelf_id):
    user = current_user()
    if not user:
        return jsonify({'error': 'Необходима авторизация'}), 401
    shelf = db.get_or_404(Shelf, shelf_id)
    if shelf.user_id != user.id:
        return jsonify({'error': 'Нет доступа'}), 403
    db.session.delete(shelf)
    db.session.commit()
    return jsonify({'message': 'Удалено'})


@app.route('/api/shelves/<int:shelf_id>/books/<int:book_id>', methods=['POST'])
def add_to_shelf(shelf_id, book_id):
    user = current_user()
    if not user:
        return jsonify({'error': 'Необходима авторизация'}), 401
    shelf = db.get_or_404(Shelf, shelf_id)
    if shelf.user_id != user.id:
        return jsonify({'error': 'Нет доступа'}), 403
    book = db.get_or_404(Book, book_id)
    if book not in shelf.books:
        shelf.books.append(book)
        db.session.commit()
    return jsonify({'message': 'Добавлено'})


@app.route('/api/shelves/<int:shelf_id>/books/<int:book_id>', methods=['DELETE'])
def remove_from_shelf(shelf_id, book_id):
    user = current_user()
    if not user:
        return jsonify({'error': 'Необходима авторизация'}), 401
    shelf = db.get_or_404(Shelf, shelf_id)
    if shelf.user_id != user.id:
        return jsonify({'error': 'Нет доступа'}), 403
    book = db.get_or_404(Book, book_id)
    if book in shelf.books:
        shelf.books.remove(book)
        db.session.commit()
    return jsonify({'message': 'Удалено'})
