import os
import json
from User.src.config import tokens_dir


class Config:
    def __init__(self, kwargs):
        self.base_path_to_share_folder = kwargs["base_path_to_share_folder"]
        self.base_share_folder_name = kwargs["base_share_folder_name"]
        self.host_list = kwargs["host_list"]


class Tokens:
    def __init__(self, kwargs):
        self.refresh_token = kwargs["refresh_token"]
        self.access_token = kwargs["access_token"]
        self.token_type = kwargs["token_type"]


def parse_config_json():
    with open('config.json', 'r', encoding='utf-8') as file:
        return Config(json.load(file))


def validate_path():
    config = parse_config_json()
    if config.base_path_to_share_folder:
        return os.path.join(config.base_path_to_share_folder, config.base_share_folder_name)
    else:
        return os.path.join(config.base_path_to_share_folder, config.base_share_folder_name)  # TODO Что то придумать


def check_or_create_share_folder(directory_path: str = None):
    """
    Проверяет, что указанная директория существует и является общедоступной.
    Если директория не существует, создаёт её и делает общедоступной.

    :return: True, если директория существует и общедоступна или была успешно создана
             False, если произошла ошибка
    """
    if not directory_path:
        directory_path = validate_path()
    try:
        # Проверяем, существует ли директория
        if not os.path.exists(directory_path):
            os.makedirs(directory_path)
            print("Создана новая папка")
            # TODO Если папка СОЗДАНА, отправлять запрос к апи (init_folder) с добавлением новой папки для чанков
        else:
            print("Папка уже существует")

    except Exception as e:
        print(f"Ошибка при обработке директории {directory_path}: {e}")
        return False


def init_folder():
    """
    api endpoint to add new folder to db
    :return:
    """
    pass


def fetch_hosts():
    """
    Проверяем указанные узлы в config.json на наличие папки .sharespace
    Если папки нет -> создаем
    TODO: на самом деле это какой то лютый костыль. Лучше будет написать отдельную прогу, которая будет сканить сеть и добавлять новые узлы в бд (прога будет чисто для сисадмина)
    :return:
    """
    for i in parse_config_json().host_list:
        check_or_create_share_folder(os.path.join(i, "/public/.sharespace"))


def save_tokens(tokens: dict) -> bool:
    try:
        with open(tokens_dir, "w", encoding='utf-8') as f:
            json.dump(tokens, f)
    except Exception as e:
        raise e
    else:
        return True


def parse_tokens():
    with open(tokens_dir, "r", encoding='utf-8') as f:
        return Tokens(json.load(f))


if __name__ == '__main__':
    check_or_create_share_folder()
