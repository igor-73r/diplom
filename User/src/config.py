import platform
import os

downloads_path = "C:\\Users\\igorm\\Downloads" if platform.system() == "Windows" else "/Users/igor/Downloads"
font_path = '../../static/fonts/NunitoSans.ttf' if platform.system() == "Windows" else "/Users/igor/Documents/UlSTU/diplom/static/fonts/NunitoSans.ttf"
download_icon = "../../static/icons/download.svg"
delete_icon = "../../static/icons/delete.svg"

tokens_dir = os.path.join(os.path.expanduser("~"), "tokens.json")

default_host = "http://127.0.0.1:8000"

auth_host = f"{default_host}/auth"
data_host = f"{default_host}/data"
