import hashlib
import os
import glob
import re


class Data:
    """
    Базовый класс для описания данных
    """
    hash_algorithm: str = 'md5'
    buffer_size: int = 65536
    file: str
    file_size: int
    chunk_size: int = 1000

    def __init__(self, path: str):
        self.file = path
        self.file_size = self._get_file_size()
        self.hash_func = self.get_hash()

    def _get_file_size(self):
        return os.path.getsize(self.file)

    def _calculate_chunk_quantity(self):
        num_chunks = self.file_size // self.chunk_size
        if self.file_size % self.chunk_size != 0:
            num_chunks += 1
        return num_chunks

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
        """
        Разбиваем файл на чанки
        :return:
        """
        if not os.path.isfile(self.file):
            print(f"Ошибка: файл '{self.file}' не существует.")
            return

        # Создаем папку для частей, если её нет
        output_dir = f"{self.file}_parts"
        os.makedirs(output_dir, exist_ok=True)

        num_of_chunk = self._calculate_chunk_quantity()

        # Читаем и записываем части
        with open(self.file, 'rb') as f:
            for i in range(num_of_chunk):
                chunk_data = f.read(self.chunk_size)
                output_path = os.path.join(output_dir, f"part_{i + 1}.bin")

                with open(output_path, 'wb') as chunk_file:
                    chunk_file.write(chunk_data)

        print(f"\nФайл успешно разделен на {num_of_chunk} частей в папке '{output_dir}'")


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


