from dotenv import load_dotenv
import os

load_dotenv()

"""TOKEN DATA"""
SECRET = os.environ.get("SECRET")
ALGORITHM = 'HS256'
ACCESS_TOKEN_EXPIRE = 30  # minutes
REFRESH_TOKEN_EXPIRE = 90  # days


base_local_path_to_share_folder = "C:\\Users\\Public"
base_net_path_to_share_folder = "\\Public"
base_share_folder_name = ".sharefolder"

# """DIRS"""
# BASE_DIR = os.getcwd()
# MEDIA_DIR = os.path.join(BASE_DIR, "media")
# PROFILE_PHOTO_DIR = os.path.join(MEDIA_DIR, "profile_photos")
