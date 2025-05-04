import requests
import os

from requests import Response

from User.src.data_splitter.Data import DataProcessing, Data
from User.src.config import auth_host, data_host
from tools import save_tokens, parse_tokens


def header_builder(content_type: str = 'application/json') -> dict | None:
    if tokens := parse_tokens():
        return {
            'Accept': 'application/json',
            'Content-Type': content_type,
            'Authorization': f'Bearer {tokens.access_token}',
        }
    else:
        return None


def get_current_user():
    response = requests.get(f"{auth_host}/get_current_user", headers=header_builder())
    return response.json()


def upload_file(file, user_id):
    file = DataProcessing(path=file)
    body = {
        "name": os.path.basename(file.file),
        "hash_func": file.hash_func,
        "size": file.file_size,
        "chunk_quantity": file.chunk_size,
        "user_owner": user_id,
    }
    response = requests.post(f"{data_host}/add_full_file",
                             json=body)

    file.file_id = response.json()["id"]
    if response.status_code == 201:
        file.split_file()


def get_files_by_user_id(user_id: int):
    response = requests.get(f"{data_host}/get_files/{user_id}")
    print(response)
    return response.json()


def download_file(file: DataProcessing, download_dir: str):
    chunks = requests.get(f"{data_host}/get_chunks/{file.file_id}")
    os.mkdir(".temp")
    for chunk in chunks.json():
        chunk_path = os.path.join(".temp", f"part_{chunk['chunk_ordinal_number']}.bin")
        with open(chunk_path, "wb+") as f:
            f.write(requests.get(f"{data_host}/download_chunk/{chunk['id']}").content)
    try:
        file.merge_files(chunks_dir="D:\\Study\\diplom\\src\\ui\\.temp", output_file=os.path.join(download_dir, file.file))
        os.rmdir(".temp")
    except Exception as e:
        import shutil
        shutil.rmtree(".temp")


def delete_file(file: DataProcessing) -> Response:
    response = requests.delete(f"{data_host}/delete_file/{file.file_id}")
    return response


def register(email: str = None, password: str = None) -> Response:
    body = {
        "email": email,
        "password": password,
    }
    response = requests.post(f"{auth_host}/register", json=body)
    if response.status_code == 201:
        return response
    else:
        return response


def auth(email: str = None, password: str = None) -> Response:
    body = {
        "username": email,
        "password": password,
    }
    response = requests.post(f"{auth_host}/token", data=body)
    if response.status_code == 200:
        save_tokens(response.json())
    return response


def create_node(pc_name: str) -> Response:
    body = {"pc_name": pc_name}
    response = requests.post(f"{data_host}/add_node", json=body)
    return response

def get_node(node: str) -> Response:
    response = requests.get(f"{data_host}/get_node/{node}")
    return response


if __name__ == '__main__':
    # auth("admin@admin.com", "admin")
    print(get_current_user())
