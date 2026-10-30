import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

# Database configuration
MYSQL_HOST = os.getenv("MYSQL_HOST", "127.0.0.1")
MYSQL_PORT = int(os.getenv("MYSQL_PORT", 3306))
MYSQL_USER = os.getenv("MYSQL_USER", "root")
MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD", "")
MYSQL_DB = os.getenv("MYSQL_DB", "tubeflow_db")

# Fallback settings
USE_SQLITE_FALLBACK = os.getenv("USE_SQLITE_FALLBACK", "true").lower() in ("true", "1", "yes")
SQLITE_DB_PATH = BASE_DIR / "tubeflow.db"

# Storage paths
STATIC_DIR = BASE_DIR / "static"
UPLOAD_DIR = STATIC_DIR / "uploads"
VIDEO_UPLOAD_DIR = UPLOAD_DIR / "videos"
THUMBNAIL_UPLOAD_DIR = UPLOAD_DIR / "thumbnails"
AVATAR_UPLOAD_DIR = UPLOAD_DIR / "avatars"
BANNER_UPLOAD_DIR = UPLOAD_DIR / "banners"

for p in [VIDEO_UPLOAD_DIR, THUMBNAIL_UPLOAD_DIR, AVATAR_UPLOAD_DIR, BANNER_UPLOAD_DIR]:
    p.mkdir(parents=True, exist_ok=True)

APP_NAME = "TubeFlow"
APP_DESCRIPTION = "High-Performance MySQL Powered YouTube Alternative"
APP_VERSION = "2.0.0"
APP_HOST = "0.0.0.0"
APP_PORT = 8000
