from dotenv import load_dotenv
import os

load_dotenv()

EMAIL = os.environ.get("EMAIL")
EMAIL_PASS = os.environ.get("EMAIL_PASS")

"""DATABASE DATA"""
DB_HOST = os.environ.get("DB_HOST")
DB_PORT = os.environ.get("DB_PORT")
DB_NAME = os.environ.get("DB_NAME")
DB_USER = os.environ.get("DB_USER")
DB_PASS = os.environ.get("DB_PASS")
DATABASE_URL = f"postgresql+asyncpg://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

"""TOKEN DATA"""
SECRET = os.environ.get("SECRET")
ALGORITHM = 'HS256'
ACCESS_TOKEN_EXPIRE = 30  # minutes
REFRESH_TOKEN_EXPIRE = 90  # days

"""DIRS"""
BASE_DIR = os.getcwd()
MEDIA_DIR = os.path.join(BASE_DIR, "media")
PROFILE_PHOTO_DIR = os.path.join(MEDIA_DIR, "profile_photos")
