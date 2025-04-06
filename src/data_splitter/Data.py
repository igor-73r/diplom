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

    def _get_file_size(self):
        return os.path.getsize(self.file)

    def _calculate_chunk_quantity(self):
        num_chunks = self.file_size // self.chunk_size
        if self.file_size % self.chunk_size != 0:
            num_chunks += 1
        return num_chunks

    def _get_hash(self):
        hasher = hashlib.new(self.hash_algorithm)
        with open(self.file, 'rb') as f:
            while True:
                data = f.read(self.buffer_size)
                if not data:
                    break
                hasher.update(data)
        return hasher.hexdigest()


class DataProcessing(Data):
    def split_file(self):
        """
        Разделяет файл на несколько кусков заданного размера.

        :param input_file: путь к входному файлу
        :param chunk_size: размер каждого куска в байтах
        """
        # Проверяем, существует ли файл
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

                print(f"Создан кусок: {output_path} (размер: {len(chunk_data)} байт)")

        print(f"\nФайл успешно разделен на {num_of_chunk} частей в папке '{output_dir}'")



    #TODO Полностью доработать (на данный момент тупо скопированный вариант из дипсика)
    def merge_files(self, input_dir, output_file, original_file=None):
        """
        Объединяет чанки с проверкой целостности

        :param input_dir: папка с чанками
        :param output_file: путь для собранного файла
        :param original_file: путь к оригиналу для проверки (опционально)
        """
        if not os.path.isdir(input_dir):
            print(f"Ошибка: директория '{input_dir}' не существует.")
            return False

        # Получаем и сортируем чанки
        chunk_files = glob.glob(os.path.join(input_dir, "part_*.bin"))
        chunk_files.sort(key=lambda x: int(re.search(r'part_(\d+)\.bin', x).group(1)))

        if not chunk_files:
            print("Ошибка: чанки не найдены")
            return False

        # Проверяем сумму размеров чанков
        total_size = sum(os.path.getsize(f) for f in chunk_files)
        print(f"Общий размер чанков: {total_size} байт")

        if original_file and os.path.exists(original_file):
            original_size = os.path.getsize(original_file)
            print(f"Размер оригинала: {original_size} байт")
            if original_size != total_size:
                print("⚠️ Предупреждение: размеры не совпадают!")

        # Собираем файл
        with open(output_file, 'wb') as out_file:
            for chunk_file in chunk_files:
                with open(chunk_file, 'rb') as cf:
                    chunk_data = cf.read()
                    out_file.write(chunk_data)
                    print(f"Добавлен {os.path.basename(chunk_file)} ({len(chunk_data)} байт)")

        # Проверка целостности через хеш
        if original_file and os.path.exists(original_file):
            print("\nПроверка целостности...")
            original_hash = calculate_file_hash(original_file)
            merged_hash = calculate_file_hash(output_file)

            print(f"Оригинальный хеш: {original_hash}")
            print(f"Полученный хеш:  {merged_hash}")

            if original_hash == merged_hash:
                print("✅ Файл собран корректно!")
                return True
            else:
                print("❌ Ошибка: хеши не совпадают!")
                return False
        else:
            print("\nФайл собран. Проверка по оригиналу невозможна.")
            return True

