import ctypes
import os

from User.src.config import base_net_path_to_share_folder, base_share_folder_name
from request_handlers import get_all_nodes


def get_free_space(network_path):
    """Получает свободное место на сетевом диске в байтах."""
    free_bytes = ctypes.c_ulonglong(0)
    total_bytes = ctypes.c_ulonglong(0)
    ctypes.windll.kernel32.GetDiskFreeSpaceExW(
        ctypes.c_wchar_p(network_path),
        None,
        ctypes.pointer(total_bytes),
        ctypes.pointer(free_bytes),
    )

    # --- 2. Считаем размер папки рекурсивно ---
    def get_folder_size(folder):
        total_size = 0
        for dirpath, _, filenames in os.walk(folder):
            for filename in filenames:
                filepath = os.path.join(dirpath, filename)
                try:
                    total_size += os.path.getsize(filepath)
                except (PermissionError, FileNotFoundError):
                    continue
        return total_size

    folder_size = get_folder_size(network_path) if os.path.exists(network_path) else 0

    return free_bytes.value, folder_size


def get_all_nodes_space_info():
    nodes = get_all_nodes()
    for i in nodes:
        i["free_space"], i["share_space_taken"] = get_free_space(f"//{i['pc_name']}{base_net_path_to_share_folder}/{base_share_folder_name}")
    return nodes


def calculate_nodes_percentage_of_total_space():
    nodes = get_all_nodes_space_info()
    total_free_space = sum([i["free_space"] for i in nodes])
    for node in nodes:
        node["part"] = round(node["free_space"] / total_free_space, 2)
    return nodes


if __name__ == '__main__':
    print(calculate_nodes_percentage_of_total_space())
