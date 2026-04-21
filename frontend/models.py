import sqlite3
import json
import hashlib
from pathlib import Path
from datetime import datetime
from dataclasses import dataclass, asdict
from typing import Optional, List
from contextlib import contextmanager

from config import DB_PATH, UPLOAD_FOLDER


@dataclass
class Book:
    id: Optional[int] = None
    title: str = ""
    author: Optional[str] = None
    file_path: Optional[str] = None
    file_format: str = ""
    file_size: int = 0
    file_hash: Optional[str] = None
    cover_path: Optional[str] = None
    description: Optional[str] = None
    year: Optional[int] = None
    language: Optional[str] = None
    page_count: Optional[int] = None
    added_date: Optional[str] = None
    metadata_json: Optional[str] = None

    def to_dict(self):
        d = asdict(self)
        d['added_date'] = self.added_date
        return d


class Database:
    def __init__(self, db_path: Path = DB_PATH):
        self.db_path = db_path

    @contextmanager
    def _connect(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

    def init_db(self):
        with self._connect() as conn:
            conn.executescript("""
                               CREATE TABLE IF NOT EXISTS books
                               (
                                   id
                                   INTEGER
                                   PRIMARY
                                   KEY
                                   AUTOINCREMENT,
                                   title
                                   TEXT
                                   NOT
                                   NULL,
                                   author
                                   TEXT,
                                   file_path
                                   TEXT
                                   NOT
                                   NULL
                                   UNIQUE,
                                   file_format
                                   TEXT
                                   NOT
                                   NULL,
                                   file_size
                                   INTEGER
                                   NOT
                                   NULL,
                                   file_hash
                                   TEXT
                                   UNIQUE,
                                   cover_path
                                   TEXT,
                                   description
                                   TEXT,
                                   year
                                   INTEGER,
                                   language
                                   TEXT,
                                   page_count
                                   INTEGER,
                                   added_date
                                   TIMESTAMP
                                   DEFAULT
                                   CURRENT_TIMESTAMP,
                                   metadata_json
                                   TEXT
                               );

                               CREATE TABLE IF NOT EXISTS book_contents
                               (
                                   id
                                   INTEGER
                                   PRIMARY
                                   KEY
                                   AUTOINCREMENT,
                                   book_id
                                   INTEGER
                                   NOT
                                   NULL
                                   REFERENCES
                                   books
                               (
                                   id
                               ) ON DELETE CASCADE,
                                   chapter_title TEXT,
                                   chapter_order INTEGER,
                                   content_text TEXT,
                                   UNIQUE
                               (
                                   book_id,
                                   chapter_order
                               )
                                   );

                               CREATE
                               VIRTUAL TABLE IF NOT EXISTS book_fts USING fts5(
                    title, author, content_text,
                    content='books',
                    content_rowid='id'
                );

                               CREATE INDEX IF NOT EXISTS idx_format ON books(file_format);
                               CREATE INDEX IF NOT EXISTS idx_author ON books(author);
                               CREATE INDEX IF NOT EXISTS idx_year ON books(year);
                               CREATE TRIGGER IF NOT EXISTS books_ai AFTER INSERT ON books
                               BEGIN
                    INSERT INTO book_fts(rowid, title, author, content_text)
                    VALUES (new.id, new.title, new.author, '');
                               END;
                               CREATE TRIGGER IF NOT EXISTS books_ad AFTER
                               DELETE
                               ON books BEGIN
                    INSERT INTO book_fts(book_fts, rowid, title, author, content_text)
                    VALUES ('delete', old.id, old.title, old.author, '');
                               END;
                               CREATE TRIGGER IF NOT EXISTS books_au AFTER
                               UPDATE ON books BEGIN
                               INSERT
                               INTO book_fts(book_fts, rowid, title, author, content_text)
                               VALUES ('delete', old.id, old.title, old.author, '');
                               INSERT INTO book_fts(rowid, title, author, content_text)
                               VALUES (new.id, new.title, new.author, '');
                               END;
                               """)

    def add_book(self, book: Book, chapters: List[tuple] = None) -> int:
        """Добавляет книгу и возвращает id. chapters: [(title, order, text), ...]"""
        with self._connect() as conn:
            cursor = conn.execute("""
                                  INSERT INTO books (title, author, file_path, file_format, file_size,
                                                     file_hash, cover_path, description, year, language,
                                                     page_count, metadata_json)
                                  VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                                  """, (
                                      book.title, book.author, book.file_path, book.file_format,
                                      book.file_size, book.file_hash, book.cover_path, book.description,
                                      book.year, book.language, book.page_count, book.metadata_json
                                  ))
            book_id = cursor.lastrowid

            if chapters:
                conn.executemany("""
                                 INSERT INTO book_contents (book_id, chapter_title, chapter_order, content_text)
                                 VALUES (?, ?, ?, ?)
                                 """, [(book_id, title, order, text) for title, order, text in chapters])

                # Обновляем FTS с полным текстом
                full_text = ' '.join(text for _, _, text in chapters)
                conn.execute("""
                             INSERT INTO book_fts(book_fts, rowid, title, author, content_text)
                             VALUES ('delete', ?, '', '', '');
                             INSERT INTO book_fts(rowid, title, author, content_text)
                             VALUES (?, ?, ?, ?);
                             """, (book_id, book_id, book.title, book.author or '', full_text))

            return book_id

    def get_book(self, book_id: int) -> Optional[Book]:
        with self._connect() as conn:
            row = conn.execute(
                "SELECT * FROM books WHERE id = ?", (book_id,)
            ).fetchone()
            return Book(**dict(row)) if row else None

    def get_book_file_path(self, book_id: int) -> Optional[Path]:
        book = self.get_book(book_id)
        if book and book.file_path:
            path = Path(book.file_path)
            if path.exists():
                return path
        return None

    def search_books(self, query: str, format_filter: str = None,
                     limit: int = 50) -> List[Book]:
        with self._connect() as conn:
            if query and query.strip():
                # Полнотекстовый поиск через FTS5
                sql = """
                      SELECT b.* \
                      FROM books b \
                               JOIN book_fts f ON b.id = f.rowid
                      WHERE book_fts MATCH ? \
                      """
                params = [query]
                if format_filter:
                    sql += " AND b.file_format = ?"
                    params.append(format_filter)
                sql += " LIMIT ?"
                params.append(limit)

                rows = conn.execute(sql, params).fetchall()
            else:
                sql = "SELECT * FROM books WHERE 1=1"
                params = []
                if format_filter:
                    sql += " AND file_format = ?"
                    params.append(format_filter)
                sql += " ORDER BY added_date DESC LIMIT ?"
                params.append(limit)
                rows = conn.execute(sql, params).fetchall()

            return [Book(**dict(row)) for row in rows]

    def list_books(self, page: int = 1, per_page: int = 20,
                   format_filter: str = None) -> tuple[List[Book], int]:
        with self._connect() as conn:
            where = "WHERE file_format = ?" if format_filter else ""
            params = [format_filter] if format_filter else []

            count_row = conn.execute(
                f"SELECT COUNT(*) FROM books {where}", params
            ).fetchone()
            total = count_row[0]

            offset = (page - 1) * per_page
            params.extend([per_page, offset])
            rows = conn.execute(
                f"SELECT * FROM books {where} ORDER BY added_date DESC LIMIT ? OFFSET ?",
                params
            ).fetchall()

            return [Book(**dict(row)) for row in rows], total

    def delete_book(self, book_id: int) -> bool:
        with self._connect() as conn:
            book = self.get_book(book_id)
            if not book:
                return False

            # Удаляем файлы
            if book.file_path:
                Path(book.file_path).unlink(missing_ok=True)
            if book.cover_path:
                Path(book.cover_path).unlink(missing_ok=True)

            conn.execute("DELETE FROM books WHERE id = ?", (book_id,))
            return True

    def get_stats(self) -> dict:
        with self._connect() as conn:
            total = conn.execute("SELECT COUNT(*) FROM books").fetchone()[0]
            formats = conn.execute("""
                                   SELECT file_format, COUNT(*) as count, SUM(file_size) as total_size
                                   FROM books
                                   GROUP BY file_format
                                   """).fetchall()
            return {
                'total_books': total,
                'by_format': {row['file_format']: {
                    'count': row['count'],
                    'size_mb': round(row['total_size'] / (1024 * 1024), 2)
                } for row in formats}
            }

    def update_fts_content(self, book_id: int, content_text: str):
        """Обновляет полнотекстовый индекс после извлечения текста."""
        with self._connect() as conn:
            book = self.get_book(book_id)
            if not book:
                return
            conn.execute("""
                         INSERT INTO book_fts(book_fts, rowid, title, author, content_text)
                         VALUES ('delete', ?, '', '', '');
                         INSERT INTO book_fts(rowid, title, author, content_text)
                         VALUES (?, ?, ?, ?);
                         """, (book_id, book_id, book.title, book.author or '', content_text))