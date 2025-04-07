import sys
import os
from PyQt6.QtWidgets import (QApplication, QMainWindow, QListWidget, QListWidgetItem,
                             QWidget, QHBoxLayout, QVBoxLayout, QPushButton, QLabel,
                             QFileDialog, QSizePolicy)
from PyQt6.QtCore import Qt, QMimeData, QSize
from PyQt6.QtGui import QDragEnterEvent, QDropEvent, QIcon, QFont, QFontDatabase, QColor

from config import font_path as fp, downloads_path


class FileManager(QMainWindow):
    file_name_len: int = 50
    global_font: QFont

    def __init__(self):
        super().__init__()
        self.setWindowTitle("File Manager")
        self.setGeometry(100, 100, 700, 500)

        font_path = fp
        QFontDatabase.addApplicationFont(font_path)
        family = QFontDatabase.applicationFontFamilies(0)
        self.global_font = QFont(family[0], 12)
        self.setFont(self.global_font)

        self.initUI()
        self.load_existing_files()
        self.setAcceptDrops(True)

    def initUI(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        self.title_label = QLabel("Drag and drop files here or use the button below:")
        layout.addWidget(self.title_label)

        self.file_list = QListWidget()
        self.file_list.setStyleSheet("""
            QListWidget {
                padding: 10px;
            }
            QListWidget::item {
                margin: 1 0;
            }
            //QListWidget::item:selected  {
            //    background-color: #595E6D;
            //    border-radius: 4px;
            //}
        """)
        layout.addWidget(self.file_list)

        self.add_button = QPushButton("Add Files")
        self.add_button.setStyleSheet("""
            QPushButton {
                padding: 8px;
            }
        """)
        self.add_button.setFont(self.global_font)
        self.add_button.clicked.connect(self.add_files_dialog)
        layout.addWidget(self.add_button)

    def load_existing_files(self):
        self.file_list.clear()
        # files = [f for f in os.listdir(path="C:\\Users\\igorm\\Downloads") if os.path.isfile(f)]
        files = [f for f in os.listdir(path=downloads_path)]
        for index, file in enumerate(files):
            self.add_file_to_list(file, index)

    def match_file_name_len(self, file_name: str) -> QLabel:
        label = QLabel(file_name[:self.file_name_len])
        if len(file_name) > self.file_name_len:
            label.setToolTip(file_name)
        return label

    def add_file_to_list(self, file_path, index):
        item = QListWidgetItem()
        self.file_list.addItem(item)
        widget = QWidget()

        even_color = QColor(87, 87, 87)
        odd_color = QColor(69, 69, 69)
        item.setBackground(even_color if index % 2 == 0 else odd_color)

        layout = QHBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)
        label = self.match_file_name_len(file_path)
        label.setStyleSheet("""
            QLabel {
                padding: 14px 9px;
                font-weight: 800;
                background-color: none;
            }
        """)
        label.setFont(self.global_font)

        delete_btn = QPushButton()
        delete_btn.setIcon(QIcon("../../static/icons/delete.svg"))
        delete_btn.setIconSize(QSize(17, 17))
        delete_btn.setFixedWidth(50)
        delete_btn.setStyleSheet("""
            QPushButton {
                height: 30px; 
                border: none;
                border-radius: 6px;
                background: #C94F4F;
                margin: 0 10px;
            }
            QPushButton:hover {
                background: #A22F2F;
            }
        """)
        delete_btn.clicked.connect(lambda _, f=file_path: self.delete_file(f))

        download_btn = QPushButton()
        download_btn.setIcon(QIcon("../../static/icons/download.svg"))
        download_btn.setIconSize(QSize(30, 30))
        download_btn.setFixedWidth(30)
        download_btn.setStyleSheet("""
            QPushButton {
                height: 30px; 
                border: none;
                border-radius: 6px;
                background: #57965C;
            }
            QPushButton:hover {
                background: #1F704A;
            }
        """)
        download_btn.clicked.connect(lambda _, f=file_path: self.download_file(f))

        layout.addWidget(label)
        layout.addWidget(download_btn)
        layout.addWidget(delete_btn)

        widget.setLayout(layout)
        item.setSizeHint(widget.sizeHint())
        self.file_list.setItemWidget(item, widget)

    def delete_file(self, file_path):
        # try:
        #     os.remove(file_path)
        #     self.load_existing_files()
        # except Exception as e:
        #     print(f"Error deleting file: {e}")
        print("DELETE")

    def download_file(self, file_path):
        print("DOWNLOAD")

    def add_files_dialog(self):
        files, _ = QFileDialog.getOpenFileNames(self, "Select Files")
        if files:
            for file_path in files:
                dest_path = os.path.basename(file_path)
                if not os.path.exists(dest_path):
                    try:
                        import shutil
                        shutil.copy(file_path, dest_path)
                        self.add_file_to_list(dest_path)
                    except Exception as e:
                        print(f"Error copying file: {e}")
                else:
                    print(f"File {dest_path} already exists")

    def dragEnterEvent(self, event: QDragEnterEvent):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event: QDropEvent):
        for url in event.mimeData().urls():
            file_path = url.toLocalFile()
            if os.path.isfile(file_path):
                dest_path = os.path.basename(file_path)
                if not os.path.exists(dest_path):
                    try:
                        import shutil
                        shutil.copy(file_path, dest_path)
                        self.add_file_to_list(dest_path)
                    except Exception as e:
                        print(f"Error copying file: {e}")
                else:
                    print(f"File {dest_path} already exists")
        event.acceptProposedAction()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = FileManager()
    window.show()
    sys.exit(app.exec())
