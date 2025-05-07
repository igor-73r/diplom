import hashlib
import os
import glob
import re
# from .request_handlers import get_all_nodes
from .tools import calculate_nodes_percentage_of_total_space
from User.src.config import data_host

class Data:
    """
    Базовый класс для описания данных
    """
    hash_algorithm: str = 'md5'
    buffer_size: int = 65536
    file: str
    file_size: int
    chunk_size: int = 10000
    file_id: int

    def __init__(self, path: str = None, kwargs: dict = None):
        if not kwargs:
            self.file = path
            self.file_size = self._get_file_size()
            self.hash_func = self.get_hash()
        else:
            self.file_id = kwargs["id"]
            self.file_size = kwargs["size"]
            self.file = kwargs["name"]
            self.hash_func = kwargs["hash_func"]
            self.chunk_size = kwargs["chunk_quantity"]

    def _get_file_size(self):
        return os.path.getsize(self.file)

    def get_hash(self, file: str = None):
        hasher = hashlib.new(self.hash_algorithm)
        with open(file if file else self.file, 'rb') as f:
            while True:
                data = f.read(self.buffer_size)
                if not data:
                    break
                hasher.update(data)
        return hasher.hexdigest()


class DataProcessing(Data):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


    def split_file(self):
        import requests
        import uuid
        """
        Разбиваем файл на чанки
        :return:
        """
        if not os.path.isfile(self.file):
            print(f"Ошибка: файл '{self.file}' не существует.")
            return


        nodes = calculate_nodes_percentage_of_total_space()
        flag = False
        with open(self.file, 'rb') as f:
            for i, node in enumerate(nodes):
                # TODO Относительный размер чанков сделал, осталось настроить пути, чтоб все нормально летело
                temp_chunk_size = int(self.file_size * node["part"]) + 10
                chunk_data = f.read(temp_chunk_size)
                body = {
                    "name": str(uuid.uuid4()),
                    "chunk_ordinal_number": i,
                    "folder_holder_id": node["id"],
                    "full_data_id": self.file_id,
                    "is_copy": False,
                }
                response = requests.post(f"{data_host}/upload_chunk?name={body['name']}"
                                         f"&chunk_ordinal_number={body['chunk_ordinal_number']}&folder_holder_id={body['folder_holder_id']}"
                                         f"&full_data_id={body['full_data_id']}&is_copy={body['is_copy']}",
                                         files={"file": chunk_data})
                if response.status_code == 201:
                    flag = True
                else:
                    return None
        return flag


    def merge_files(self, chunks_dir, output_file):
        """
        Объединяет чанки с проверкой целостности

        :param chunks_dir: папка с чанками
        :param output_file: путь для собранного файла
        """
        if not os.path.isdir(chunks_dir):
            print(f"Ошибка: директория '{chunks_dir}' не существует.")
            return False

        # Получаем и сортируем чанки
        chunk_files = glob.glob(os.path.join(chunks_dir, "part_*.bin"))
        chunk_files.sort(key=lambda x: int(re.search(r'part_(\d+)\.bin', x).group(1)))

        if not chunk_files:
            print("Ошибка: чанки не найдены")
            return False

        # Проверяем сумму размеров чанков
        total_size = sum(os.path.getsize(f) for f in chunk_files)
        print(f"Общий размер чанков: {total_size} байт")

        if self.file_size:
            if self.file_size != total_size:
                print("⚠️ Предупреждение: размеры не совпадают!")

        # Собираем файл
        with open(output_file, 'wb') as out_file:
            for chunk_file in chunk_files:
                with open(chunk_file, 'rb') as cf:
                    chunk_data = cf.read()
                    out_file.write(chunk_data)

        # Проверка целостности
        if self.hash_func:
            print("\nПроверка целостности...")
            original_hash = self.hash_func
            merged_hash = self.get_hash(output_file)

            if original_hash == merged_hash:
                print("✅ Файл собран корректно!")
                return True
            else:
                print("❌ Ошибка: хеши не совпадают!")
                return False
        else:
            print("\nФайл собран. Проверка по оригиналу невозможна.")
            return True


if __name__ == '__main__':
    png = DataProcessing(path="D:\\Study\\diplom\\test_dir\\before\\bin.png")
    mp3 = DataProcessing(path="D:\\Study\\diplom\\test_dir\\before\\Adele_-_Skyfall_48385024.mp3")
    docx = DataProcessing(path="D:\\Study\\diplom\\test_dir\\before\\kursovayaISE_OBRAZETs.docx")

    png.split_file()
    mp3.split_file()
    docx.split_file()

    png.merge_files(chunks_dir="D:\\Study\\diplom\\test_dir\\before\\bin.png_parts",
                    output_file="D:\\Study\\diplom\\test_dir\\after\\bin.png")
    mp3.merge_files(chunks_dir="D:\\Study\\diplom\\test_dir\\before\\Adele_-_Skyfall_48385024.mp3_parts",
                    output_file="D:\\Study\\diplom\\test_dir\\after\\Adele_-_Skyfall_48385024.mp3")
    docx.merge_files(chunks_dir="D:\\Study\\diplom\\test_dir\\before\\kursovayaISE_OBRAZETs.docx_parts",
                     output_file="D:\\Study\\diplom\\test_dir\\after\\kursovayaISE_OBRAZETs.docx")


