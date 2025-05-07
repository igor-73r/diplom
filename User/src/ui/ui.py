import sys
import os

import requests
from PyQt6.QtWidgets import (QApplication, QMainWindow, QListWidget, QListWidgetItem,
                             QWidget, QHBoxLayout, QVBoxLayout, QPushButton, QLabel,
                             QFileDialog, QLineEdit, QMessageBox, QDialog, QTabWidget, QFrame)
from PyQt6.QtCore import QSize
from PyQt6.QtGui import QDragEnterEvent, QDropEvent, QIcon, QFont, QFontDatabase, QColor

from User.src.config import font_path as fp, download_icon, delete_icon

from request_handlers import *
import json
from PyQt6.QtCore import pyqtSignal
from tools import check_or_create_share_folder


class LoginWindow(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent_window = parent
        self.setWindowTitle("Авторизация")
        self.setFixedSize(300, 200)

        layout = QVBoxLayout(self)

        # Email поле
        self.email_label = QLabel("Email:")
        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("Введите ваш email")

        # Пароль поле
        self.password_label = QLabel("Пароль:")
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Введите пароль")
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)

        # Кнопки входаи регистрации
        buttons = QHBoxLayout(self)
        self.login_button = QPushButton("Войти")
        self.login_button.clicked.connect(self.handle_login)
        self.reg_button = QPushButton("Регистрация")
        self.reg_button.clicked.connect(self.handle_reg)
        buttons.addWidget(self.login_button)
        buttons.addWidget(self.reg_button)

        # Добавляем элементы
        layout.addWidget(self.email_label)
        layout.addWidget(self.email_input)
        layout.addWidget(self.password_label)
        layout.addWidget(self.password_input)
        layout.addLayout(buttons)


    def handle_reg(self):
        from request_handlers import register
        email = self.email_input.text()
        password = self.password_input.text()
        response = register(email, password)
        if response.status_code == 201:
            response = auth(email, password)
        if response.status_code == 200:
            self.accept()  # Закрываем окно после успешного входа


    def handle_login(self):
        from request_handlers import auth
        email = self.email_input.text()
        password = self.password_input.text()
        response = auth(email, password)
        if response.status_code == 200:
            self.accept()  # Закрываем окно после успешного входа


class ShareSpace(QMainWindow):
    file_name_len: int = 50
    global_font: QFont
    user: dict

    def __init__(self):
        super().__init__()
        self.init_share_folder()
        self.setWindowTitle("ShareSpace")
        self.setGeometry(100, 100, 700, 500)

        QFontDatabase.addApplicationFont(fp)
        family = QFontDatabase.applicationFontFamilies(0)
        self.global_font = QFont(family[0], 12)
        self.setFont(self.global_font)

        self.fetch_window()
        self.setAcceptDrops(True)

    def fetch_window(self):
        self.user = self.get_user()
        self.initUI()
        self.load_existing_files()

    @staticmethod
    def init_share_folder():
        return check_or_create_share_folder()

    def initUI(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        # Создаем виджет вкладок
        self.tab_widget = QTabWidget()
        self.tab_widget.tabBarClicked.connect(self.on_tab_changed)
        layout.addWidget(self.tab_widget)

        self.main_tab = QWidget()
        self.second_tab = QWidget()
        self.auth_tab = QWidget()
        self.settings_tab = QWidget()
        self.setup_main_tab()
        self.setup_second_tab()
        self.setup_auth_tab()
        self.setup_settings_tab()

        # Первая вкладка (основная)
        if self.user:
            self.tab_widget.addTab(self.main_tab, "Файлы")
            self.tab_widget.addTab(self.second_tab, "Информация о системе")
            self.tab_widget.addTab(self.settings_tab, "Настройки")
        else:
            self.tab_widget.addTab(self.main_tab, "Файлы")
            self.tab_widget.addTab(self.auth_tab, "Авторизация")

    def setup_settings_tab(self):
        pass

    def setup_auth_tab(self):
        # Основной layout
        main_layout = QHBoxLayout(self.settings_tab)
        main_layout.setSpacing(30)
        main_layout.setContentsMargins(50, 20, 50, 20)

        # Форма входа
        login_frame = QFrame()
        login_frame.setFrameShape(QFrame.Shape.StyledPanel)
        login_layout = QVBoxLayout(login_frame)
        login_layout.setContentsMargins(20, 20, 20, 20)
        login_layout.setSpacing(15)

        login_title = QLabel("Вход в систему")
        login_title.setStyleSheet("font-size: 18px; font-weight: bold;")

        self.login_email = QLineEdit()
        self.login_email.setPlaceholderText("Email")

        self.login_password = QLineEdit()
        self.login_password.setPlaceholderText("Пароль")
        self.login_password.setEchoMode(QLineEdit.EchoMode.Password)

        self.login_btn = QPushButton("Войти")
        self.login_btn.setStyleSheet("""
                    QPushButton {
                        background-color: #4CAF50;
                        color: white;
                        border: none;
                        padding: 10px;
                        font-weight: bold;
                    }
                    QPushButton:hover {
                        background-color: #45a049;
                    }
                """)

        login_layout.addWidget(login_title)
        login_layout.addWidget(QLabel("Email:"))
        login_layout.addWidget(self.login_email)
        login_layout.addWidget(QLabel("Пароль:"))
        login_layout.addWidget(self.login_password)
        login_layout.addWidget(self.login_btn)
        login_layout.addStretch()

        # Форма регистрации
        register_frame = QFrame()
        register_frame.setFrameShape(QFrame.Shape.StyledPanel)
        register_layout = QVBoxLayout(register_frame)
        register_layout.setContentsMargins(20, 20, 20, 20)
        register_layout.setSpacing(15)

        register_title = QLabel("Регистрация")
        register_title.setStyleSheet("font-size: 18px; font-weight: bold;")

        self.register_email = QLineEdit()
        self.register_email.setPlaceholderText("Email")

        self.register_password = QLineEdit()
        self.register_password.setPlaceholderText("Пароль")
        self.register_password.setEchoMode(QLineEdit.EchoMode.Password)

        self.register_confirm_password = QLineEdit()
        self.register_confirm_password.setPlaceholderText("Повторите пароль")
        self.register_confirm_password.setEchoMode(QLineEdit.EchoMode.Password)

        self.register_btn = QPushButton("Зарегистрироваться")
        self.register_btn.setStyleSheet("""
                    QPushButton {
                        background-color: #2196F3;
                        color: white;
                        border: none;
                        padding: 10px;
                        font-weight: bold;
                    }
                    QPushButton:hover {
                        background-color: #0b7dda;
                    }
                """)

        register_layout.addWidget(register_title)
        register_layout.addWidget(QLabel("Email:"))
        register_layout.addWidget(self.register_email)
        register_layout.addWidget(QLabel("Пароль:"))
        register_layout.addWidget(self.register_password)
        register_layout.addWidget(QLabel("Повторите пароль:"))
        register_layout.addWidget(self.register_confirm_password)
        register_layout.addWidget(self.register_btn)
        register_layout.addStretch()

        # Добавляем обе формы в основной layout
        main_layout.addWidget(login_frame)
        main_layout.addWidget(register_frame)

        # Установка минимальных размеров для форм
        login_frame.setMinimumWidth(300)
        register_frame.setMinimumWidth(300)

    def on_tab_changed(self, index):
        """Обновляет содержимое вкладки при переключении"""
        if index == 0:  # Вкладка "Файлы"
            pass
        elif index == 1:  # Вкладка "Информация о системе"
            if hasattr(self.second_tab, 'layout'):
                QWidget().setLayout(self.second_tab.layout())
            self.setup_second_tab()


    def setup_second_tab(self):
        from User.src.data_splitter.tools import get_all_nodes_space_info

        layout = QVBoxLayout(self.second_tab)

        # Получаем информацию о всех узлах
        nodes_info = get_all_nodes_space_info()

        # Вычисляем общие параметры системы
        total_free = sum(node['free_space'] for node in nodes_info)
        total_share = sum(node['share_space_taken'] for node in nodes_info)

        # Создаем виджет для отображения общей информации
        summary_widget = QWidget()
        summary_widget.setStyleSheet("""
            QWidget {
                background-color: #424242;
                padding: 10px;
                border-radius: 5px;
                margin-bottom: 10px;
            }
            QLabel {
                font-weight: bold;
            }
        """)

        summary_layout = QVBoxLayout(summary_widget)

        def beautiful_size(size: int):
            if size / (1024 ** 2) >= 1024:
                return f"{size / (1024 ** 3):.2f} GB"
            return f"{size / (1024 ** 2):.2f} MB"

        # Добавляем метки с общей информацией
        # total_free_label = QLabel(f"Общее свободное пространство: {total_free / (1024 ** 2):.2f} MB")
        # total_share_label = QLabel(f"Общее занятое пространство в ShareSpace: {total_share / (1024 ** 2):.2f} MB")
        total_free_label = QLabel(f"Общее свободное пространство: {beautiful_size(total_free)}")
        total_share_label = QLabel(f"Общее занятое пространство в ShareSpace: {beautiful_size(total_share)}")

        summary_layout.addWidget(total_free_label)
        summary_layout.addWidget(total_share_label)
        layout.addWidget(summary_widget)

        # Создаем список для отображения информации о каждом узле
        self.nodes_list = QListWidget()
        self.nodes_list.setStyleSheet("""
            QListWidget {
                padding: 5px;
            }
            QListWidget::item {
                margin: 2px 0;
                background-color: #595959;
                border-radius: 3px;
            }
        """)

        # Добавляем информацию о каждом узле в список
        for node in nodes_info:
            item = QListWidgetItem()
            self.nodes_list.addItem(item)

            widget = QWidget()
            node_layout = QHBoxLayout(widget)

            # Информация об узле
            node_info = QLabel(
                f"{node['pc_name']} (ID: {node['id']}): "
                f"Свободно: {beautiful_size(node['free_space'])}, "
                f"Занято в ShareSpace: {beautiful_size(node['share_space_taken'])}"
            )

            node_layout.addWidget(node_info)
            widget.setLayout(node_layout)

            item.setSizeHint(widget.sizeHint())
            self.nodes_list.setItemWidget(item, widget)

        layout.addWidget(self.nodes_list)



    def setup_main_tab(self):
        layout = QVBoxLayout(self.main_tab)

        header = QHBoxLayout()
        self.title_label = QLabel("Перенесите файл, или нажмите на кнопку ниже:")
        self.auth_button = QPushButton()
        if self.user:
            self.auth_button.setText("Выход")
            self.auth_button.clicked.connect(self.auth_exit)
        else:
            self.auth_button.setText("Авторизация")
            self.auth_button.clicked.connect(self.show_login_window)
        self.auth_button.setFixedWidth(150)
        header.addWidget(self.auth_button)
        header.addStretch()
        header.addWidget(self.title_label)

        layout.addLayout(header)

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

    def auth_exit(self):
        from tools import save_tokens
        save_tokens(tokens={"access_token": "", "refresh_token": "", "token_type": ""})
        self.fetch_window()

    @staticmethod
    def get_user():
        from request_handlers import get_current_user
        user = get_current_user()
        try:
            if user["detail"] == "UNAUTHORIZED":
                return None
        except KeyError:
            return user

    def show_login_window(self):
        login_dialog = LoginWindow(self)  # self передается как parent
        if login_dialog.exec() == QDialog.DialogCode.Accepted:
            self.fetch_window()

    def load_existing_files(self):
        self.file_list.clear()
        if self.user:
            files = [DataProcessing(kwargs=f) for f in get_files_by_user_id(self.user["id"])]
            for file in files:
                self.add_file_to_list(file)

    def match_file_name_len(self, file_name: str) -> QLabel:
        label = QLabel(file_name[:self.file_name_len])
        if len(file_name) > self.file_name_len:
            label.setToolTip(file_name)
        return label

    def add_file_to_list(self, file: DataProcessing):
        file_path = file.file
        index = len(self.file_list) + 1
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
        delete_btn.setIcon(QIcon(delete_icon))
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
        delete_btn.clicked.connect(lambda _, f=file: self.delete_file(f))

        download_btn = QPushButton()
        download_btn.setIcon(QIcon(download_icon))
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
        download_btn.clicked.connect(lambda _, f=file: self.download_file(f))

        layout.addWidget(label)
        layout.addWidget(download_btn)
        layout.addWidget(delete_btn)

        widget.setLayout(layout)
        item.setSizeHint(widget.sizeHint())
        self.file_list.setItemWidget(item, widget)

    def delete_file(self, file: DataProcessing):
        from request_handlers import delete_file as df
        df(file)
        self.load_existing_files()

    def download_file(self, file: DataProcessing):
        from request_handlers import download_file as df
        down_dir = str(QFileDialog.getExistingDirectory(self, "Select Directory"))
        df(file, download_dir=down_dir)

    def add_files_dialog(self):
        files, _ = QFileDialog.getOpenFileNames(self, "Select Files")
        if files:
            for file_path in files:
                try:
                    upload_file(file_path, self.user["id"])
                    self.load_existing_files()
                except Exception as e:
                    raise e

    def dragEnterEvent(self, event: QDragEnterEvent):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event: QDropEvent):
        for url in event.mimeData().urls():
            file_path = url.toLocalFile()
            if os.path.isfile(file_path):
                try:
                    upload_file(file_path, self.user["id"])
                    self.load_existing_files()
                except Exception as e:
                    raise e
        event.acceptProposedAction()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ShareSpace()
    window.show()
    sys.exit(app.exec())