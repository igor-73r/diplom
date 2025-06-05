import datetime
import sys
import os

import requests
from PyQt6.QtWidgets import (QApplication, QMainWindow, QListWidget, QListWidgetItem,
                             QWidget, QHBoxLayout, QVBoxLayout, QPushButton, QLabel,
                             QFileDialog, QLineEdit, QMessageBox, QDialog, QTabWidget, QFrame)
from PyQt6.QtCore import QSize
from PyQt6.QtGui import QDragEnterEvent, QDropEvent, QIcon, QFont, QFontDatabase, QColor

from User.src.config import font_path as fp, download_icon, delete_icon, restore_icon, move_to_bin_icon

from request_handlers import *
import json
from PyQt6.QtCore import pyqtSignal
from PyQt6.QtCore import Qt
from tools import check_or_create_share_folder


class ChangePasswordDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()

    def setup_ui(self):
        self.setWindowTitle("Изменение пароля")
        self.setFixedWidth(300)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        # Поля ввода
        self.old_password = QLineEdit()
        self.old_password.setPlaceholderText("Старый пароль")
        self.old_password.setEchoMode(QLineEdit.EchoMode.Password)

        self.new_password = QLineEdit()
        self.new_password.setPlaceholderText("Новый пароль")
        self.new_password.setEchoMode(QLineEdit.EchoMode.Password)

        self.confirm_password = QLineEdit()
        self.confirm_password.setPlaceholderText("Повторите новый пароль")
        self.confirm_password.setEchoMode(QLineEdit.EchoMode.Password)

        # Кнопка изменения
        self.change_btn = QPushButton("Изменить")
        self.change_btn.clicked.connect(self.change_password)

        # Добавляем элементы
        layout.addWidget(QLabel("Старый пароль:"))
        layout.addWidget(self.old_password)
        layout.addWidget(QLabel("Новый пароль:"))
        layout.addWidget(self.new_password)
        layout.addWidget(QLabel("Повторите пароль:"))
        layout.addWidget(self.confirm_password)
        layout.addWidget(self.change_btn)

    def change_password(self):
        old_pass = self.old_password.text()
        new_pass = self.new_password.text()
        confirm_pass = self.confirm_password.text()
        from request_handlers import update_password

        if not old_pass or not new_pass or not confirm_pass:
            QMessageBox.warning(self, "Ошибка", "Все поля должны быть заполнены")
            return

        if new_pass != confirm_pass:
            QMessageBox.warning(self, "Ошибка", "Пароли не совпадают")
            return

        if update_password(old_pass, new_pass, confirm_pass).status_code == 200:
            # Здесь должна быть логика изменения пароля
            QMessageBox.information(self, "Успех", "Пароль успешно изменен")
            self.accept()
        else:
            QMessageBox.warning(self, "Ошибка", "Что-то пошло не так")
        self.close()


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
        self.rec_bin_tab = QWidget()
        self.setup_main_tab()
        self.setup_second_tab()
        self.setup_auth_tab()
        self.setup_rec_bin_tab()

        # Первая вкладка (основная)
        if self.user:
            self.setup_settings_tab()
            self.tab_widget.addTab(self.main_tab, "Файлы")
            self.tab_widget.addTab(self.second_tab, "Информация о системе")
            self.tab_widget.addTab(self.settings_tab, "Настройки")
            self.tab_widget.addTab(self.rec_bin_tab, "Корзина")
        else:
            # self.tab_widget.addTab(self.main_tab, "Файлы")
            self.tab_widget.addTab(self.auth_tab, "Авторизация")

    def setup_settings_tab(self):
        main_layout = QVBoxLayout(self.settings_tab)
        # main_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.setContentsMargins(20, 50, 20, 50)
        main_layout.setSpacing(30)

        # Блок изменения email
        email_layout = QHBoxLayout()
        email_label = QLabel("Email:")

        self.email_input = QLineEdit()
        self.email_input.setText(self.user.get('email'))

        self.apply_email_btn = QPushButton("Применить")
        self.apply_email_btn.clicked.connect(self.update_email)
        self.apply_email_btn.setFixedWidth(180)

        email_layout.addWidget(email_label)
        email_layout.addWidget(self.email_input)
        email_layout.addWidget(self.apply_email_btn)

        main_layout.addLayout(email_layout)

        # Блок добавления узла (только для админа)
        if self.user.get('is_admin', False):
            node_layout = QHBoxLayout()
            node_label = QLabel("Добавление узла:")

            self.node_input = QLineEdit()
            self.node_input.setPlaceholderText("Введите имя узла")

            self.add_node_btn = QPushButton("Добавить")
            self.add_node_btn.clicked.connect(self.add_node)
            self.add_node_btn.setFixedWidth(180)

            node_layout.addWidget(node_label)
            node_layout.addWidget(self.node_input)
            node_layout.addWidget(self.add_node_btn)

            main_layout.addLayout(node_layout)

        # Кнопка изменения пароля
        self.change_password_btn = QPushButton("Изменить пароль")
        self.change_password_btn.clicked.connect(self.show_change_password_dialog)
        main_layout.addWidget(self.change_password_btn)

        # Кнопка выхода
        self.logout_btn = QPushButton("Выход")
        self.logout_btn.clicked.connect(self.auth_exit)
        main_layout.addWidget(self.logout_btn)

        # Добавляем растягивающийся элемент для выравнивания вверху
        main_layout.addStretch()

    def update_email(self):
        new_email = self.email_input.text()
        from request_handlers import update_email
        if update_email(new_email).status_code == 200:
            QMessageBox.information(self, "Успех", f"Email изменен на: {new_email}")
        else:
            QMessageBox.information(self, "Ошибка", f"Указан некорректный формат")

    def add_node(self):
        node_name = self.node_input.text()
        if node_name:
            from request_handlers import create_node
            if create_node(node_name).status_code == 201:
                QMessageBox.information(self, "Успех", f"Узел '{node_name}' добавлен")
            else:
                QMessageBox.information(self, "Ошибка", f"Такой узел уже существует")
            self.node_input.clear()
        else:
            QMessageBox.warning(self, "Ошибка", "Введите имя узла")

    def show_change_password_dialog(self):
        dialog = ChangePasswordDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.auth_exit()

    def setup_auth_tab(self):
        # Основной layout
        main_layout = QHBoxLayout(self.auth_tab)
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

        def handle_reg():
            from request_handlers import register
            email = self.register_email.text()
            password = self.register_password.text()
            if password == self.register_confirm_password.text():
                response = register(email, password)
                if response.status_code == 201:
                    response = auth(email, password)
                if response.status_code == 200:
                    self.fetch_window()
                else:
                    QMessageBox.warning(self, "Ошибка", f"Такой пользователь уже существует")

        def handle_login():
            from request_handlers import auth
            email = self.login_email.text()
            password = self.login_password.text()
            response = auth(email, password)
            if response.status_code == 200:
                self.fetch_window()
            else:
                QMessageBox.warning(self, "Ошибка", f"Неверные данные пользователя")

        self.login_btn.clicked.connect(handle_login)
        self.register_btn.clicked.connect(handle_reg)

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
        self.title_label = QLabel("Перенесите файл, или нажмите на кнопку")
        self.add_button = QPushButton("Загрузить файл")
        self.add_button.clicked.connect(self.add_files_dialog)
        self.add_button.setFixedWidth(150)
        header.addWidget(self.title_label)
        header.addStretch()
        header.addWidget(self.add_button)

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

    def setup_rec_bin_tab(self):
        layout = QVBoxLayout(self.rec_bin_tab)

        header = QHBoxLayout()
        self.title_label = QLabel("Корзина")
        header.addWidget(self.title_label)

        layout.addLayout(header)

        self.file_in_rec_list = QListWidget()
        self.file_in_rec_list.setStyleSheet("""
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
        layout.addWidget(self.file_in_rec_list)

    def auth_exit(self):
        from tools import save_tokens
        save_tokens(tokens={"access_token": "", "refresh_token": "", "token_type": ""})
        self.fetch_window()

    @staticmethod
    def get_user():
        from request_handlers import get_current_user
        user = get_current_user()
        # print(user)
        try:
            if user["detail"] == "UNAUTHORIZED":
                return None
        except KeyError:
            return user

    def load_existing_files(self):
        self.file_list.clear()
        self.file_in_rec_list.clear()
        if self.user:
            files = [DataProcessing(kwargs=f) for f in get_files_by_user_id(self.user["id"])]
            for file in files:
                if file.delete_time:
                    self.add_file_to_list(file, in_bin=True)
                else:
                    self.add_file_to_list(file)

    def match_file_name_len(self, file_name: str) -> QLabel:
        label = QLabel(file_name[:self.file_name_len])
        if len(file_name) > self.file_name_len:
            label.setToolTip(file_name)
        return label

    def add_file_to_list(self, file: DataProcessing, in_bin=False):
        if file.delete_time and file.delete_time < int(datetime.datetime.now().timestamp()):
            self.delete_file(file)
            return

        file_path = file.file

        file_widget = self.file_in_rec_list if in_bin else self.file_list

        index = len(file_widget) + 1
        item = QListWidgetItem()
        file_widget.addItem(item)
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

        restore_btn = QPushButton()
        restore_btn.setIcon(QIcon(restore_icon))
        restore_btn.setIconSize(QSize(17, 17))
        restore_btn.setFixedWidth(50)
        restore_btn.setStyleSheet("""
            QPushButton {
                height: 30px; 
                border: none;
                border-radius: 6px;
                background: #57965C;
                margin: 0 10px;
            }
            QPushButton:hover {
                background: #1F704A;
            }
        """)
        restore_btn.clicked.connect(lambda _, f=file: self.restore_file(f))

        move_to_bin_btn = QPushButton()
        move_to_bin_btn.setIcon(QIcon(move_to_bin_icon))
        move_to_bin_btn.setIconSize(QSize(17, 17))
        move_to_bin_btn.setFixedWidth(50)
        move_to_bin_btn.setStyleSheet("""
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
        move_to_bin_btn.clicked.connect(lambda _, f=file: self.move_to_bin_file(f))

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
        if in_bin:
            layout.addWidget(restore_btn)
            layout.addWidget(delete_btn)
        else:
            layout.addWidget(download_btn)
            layout.addWidget(move_to_bin_btn)

        widget.setLayout(layout)
        item.setSizeHint(widget.sizeHint())
        file_widget.setItemWidget(item, widget)

    def restore_file(self, file: DataProcessing):
        from request_handlers import restore_from_rec_bin as df
        df(file)
        self.load_existing_files()

    def move_to_bin_file(self, file: DataProcessing):
        from request_handlers import move_to_rec_bin as df
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle("Подтверждение")
        msg_box.setText("Вы уверены, что хотите переместить файл в корзину? Файлы, которые перемещены в корзину, будут окончательно удалены через сутки.")
        msg_box.setIcon(QMessageBox.Icon.Question)

        msg_box.setStandardButtons(
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        msg_box.setDefaultButton(QMessageBox.StandardButton.No)

        reply = msg_box.exec()

        if reply == QMessageBox.StandardButton.Yes:
            df(file)
            self.load_existing_files()

    def delete_file(self, file: DataProcessing):
        from request_handlers import delete_file as df
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle("Подтверждение")
        msg_box.setText("Вы уверены, что хотите удалить файл?")
        msg_box.setIcon(QMessageBox.Icon.Question)

        msg_box.setStandardButtons(
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        msg_box.setDefaultButton(QMessageBox.StandardButton.No)

        reply = msg_box.exec()

        if reply == QMessageBox.StandardButton.Yes:
            df(file)
            self.load_existing_files()

    def download_file(self, file: DataProcessing):
        from request_handlers import download_file as df
        down_dir = str(QFileDialog.getExistingDirectory(self, "Select Directory"))
        f = df(file, download_dir=down_dir)
        print(f)
        if f is True:
            QMessageBox.information(self, "Успех", "Файл собран корректно")
        else:
            QMessageBox.warning(self, "Ошибка", "При сборке файла произошла ошибка")

    def add_files_dialog(self):
        files, _ = QFileDialog.getOpenFileNames(self, "Select Files")
        if files:
            for file_path in files:
                try:
                    if os.path.getsize(file_path) == 0:
                        QMessageBox.warning(self, "Внимание", "Файл, который вы пытаетесь загрузить, имеет размер 0 байт")
                        return
                    response = upload_file(file_path, self.user["id"])
                    if type(response) == bool and response is True:
                        self.load_existing_files()
                        QMessageBox.information(self, "Успех", "Файл загружен корректно")
                except Exception as e:
                    QMessageBox.warning(self, "Ошибка", "Что то пошло не так")
                    raise e

    def dragEnterEvent(self, event: QDragEnterEvent):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event: QDropEvent):
        for url in event.mimeData().urls():
            file_path = url.toLocalFile()
            if os.path.isfile(file_path):
                try:
                    if os.path.getsize(file_path) == 0:
                        QMessageBox.warning(self, "Внимание", "Файл, который вы пытаетесь загрузить, имеет размер 0 байт")
                        return
                    response = upload_file(file_path, self.user["id"])
                    if type(response) == bool and response is True:
                        self.load_existing_files()
                        QMessageBox.information(self, "Успех", "Файл загружен корректно")
                except Exception as e:
                    QMessageBox.warning(self, "Ошибка", "Что то пошло не так")
                    raise e
        event.acceptProposedAction()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ShareSpace()
    window.show()
    sys.exit(app.exec())
