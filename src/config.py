import platform


downloads_path = "C:\\Users\\igorm\\Downloads" if platform.system() == "Windows" else "/Users/igor/Downloads"
font_path = '../static/fonts/NunitoSans.ttf' if platform.system() == "Windows" else "/Users/igor/Documents/UlSTU/diplom/static/fonts/NunitoSans.ttf"
download_icon = "../static/icons/download.svg"
delete_icon = "../static/icons/delete.svg"
