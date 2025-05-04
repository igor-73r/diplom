import ctypes

import requests
import psutil
import os

from requests import Response

from User.src.config import auth_host, data_host, base_net_path_to_share_folder, base_share_folder_name


def upload_chunk():
    pass

def get_all_nodes() -> dict | None:
    response = requests.get(f"{data_host}/get_nodes")
    if response.status_code == 200:
        return response.json()
    return None


