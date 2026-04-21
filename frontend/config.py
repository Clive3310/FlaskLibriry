from pathlib import Path

BASE_DIR = Path(__file__).parent
UPLOAD_FOLDER = BASE_DIR / "uploads"
THUMBNAIL_FOLDER = BASE_DIR / "thumbnails"
DB_PATH = BASE_DIR / "library.db"

UPLOAD_FOLDER.mkdir(exist_ok=True)
THUMBNAIL_FOLDER.mkdir(exist_ok=True)

ALLOWED_FORMATS = {'epub', 'fb2', 'docx'}
MAX_FILE_SIZE = 50 * 1024 * 1024  # 50 MB