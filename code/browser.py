import sys
import socket
import secrets
import json
import os
import random
import bcrypt
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtWebEngineWidgets import *

import smtplib 
from PyQt5.QtGui import QPixmap
from email.mime.text import MIMEText
from main import runvirtualmouse, stopvirtualmouse


class MainWindow1(QMainWindow):
    def __init__(self):
        super(MainWindow1, self).__init__()
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QHBoxLayout()
        central_widget.setLayout(main_layout)

        left_frame = QFrame()
        self.left_layout = QHBoxLayout()
        left_frame.setLayout(self.left_layout)

        image_label = QLabel()
        image_label.setPixmap(QPixmap('logo5.png').scaled(398, 332))
        self.left_layout.addWidget(image_label)

        right_frame = QFrame()
        self.right_layout = QStackedLayout()
        right_frame.setLayout(self.right_layout)

        login_page = LoginWindow(self)
        self.right_layout.addWidget(login_page)

        register_page = RegisterWindow(self)
        self.right_layout.addWidget(register_page)

        self.right_layout.setCurrentIndex(0)

        main_layout.addWidget(left_frame)
        main_layout.addWidget(right_frame)
        
    def show_login_window(self):
        self.login_window = LoginWindow(self)
        self.login_window.show()

    def show_register_window(self):
        self.register_window = RegisterWindow(self)
        self.register_window.show()


class MainWindow(QWidget):
    def __init__(self, parent = None):
        super(MainWindow, self).__init__(parent)
        self.users = self.load_users()
        self.bookmarks = {}
        self.show_interface_window()
        
    def load_users(self):
        try:
            with open('users.json', 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return {}
        except json.JSONDecodeError:
            return {}
        
    def load_history(self, username):
        try:
            with open(f'{username}_history.json', 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return []
        except json.JSONDecodeError:
            return []
        
    def load_bookmarks(self, username):
        file_path = f'{username}_bookmarks.json'
        if not os.path.exists(file_path):
            return []
        else:
            with open(file_path, 'r') as f:
                try:
                    data = json.load(f)
                    return data.get(username, [])
                except (ValueError, FileNotFoundError):
                    return []

    def save_users(self):
        with open('users.json', 'w') as f:
            json.dump(self.users, f)

    def show_login_window(self):
        self.login_window = LoginWindow(self)
        self.login_window.show()

    def show_interface_window(self):
        self.show_interface = MainWindow1()
        self.show_interface.show()

    def show_register_window(self):
        self.register_window = RegisterWindow(self)
        self.register_window.show()
    
    def save_history(self, username, history):
        with open(f'{username}_history.json', 'w') as f:
            json.dump(history, f)

    def save_bookmarks(self, username, bookmarks):
        file_path = f'{username}_bookmarks.json'
        if not os.path.exists(file_path):
            data = {}
        else:
            with open(file_path, 'r') as f:
                try:
                    data = json.load(f)
                    if not isinstance(data, dict):
                        data = {}
                except (ValueError, FileNotFoundError):
                    data = {}
    
        data[username] = bookmarks
        with open(file_path, 'w') as f:
            try:
                json.dump(data, f)
            except Exception as e:
                print(f"Error saving bookmarks: {e}")

    def show_browser(self,username):
        print("Showing browser window")
        if hasattr(self, 'browser_window') and self.browser_window.isVisible():
            self.browser_window.close()
        self.browser_window = BrowserWindow(self, username)
        print("Browser window created")
        self.browser_window.show()
        print("Browser window shown")

    def save_data(self):
        if hasattr(self.browser_window, 'username') and self.browser_window.username is not None:
            username = self.browser_window.username
        if isinstance(self.browser_window.user_bookmarks, dict):
            bookmarks = self.browser_window.user_bookmarks.get(username, [])
        else:
            bookmarks = []
        # Save the bookmarks to a file or database
        with open('bookmarks.txt', 'w') as file:
            for bookmark in bookmarks:
                file.write(bookmark + '\n')
        print(f"Bookmarks saved for {username}")
        pass


class BrowserWindow(QMainWindow):
    def __init__(self, parent=None,username=""):
        super(BrowserWindow, self).__init__(parent)
        if not isinstance(parent, (QWidget, type(None))):
            raise TypeError("Parent must be a QWidget or None")
        self.parent = parent
        self.closing_bookmarks_or_history = False
        self.username = username
        self.browser = QWebEngineView()
        self.bookmarks_list = QListWidget()
        self.history_list = QListWidget()
        self.browser.setUrl(QUrl('https://google.com'))
        self.setCentralWidget(self.browser)
        self.showMaximized()
        self.setStyleSheet("font-size: 12pt;")
        self.bookmarks = self.parent.load_bookmarks(self.username)
        self.history = self.parent.load_history(self.username)
        self.user_bookmarks = {username: []}
        self.user_history = {username: []}
        self.last_url = None
        self.closeEvent = self.close_event

        self.navbar = QToolBar()
        self.addToolBar(self.navbar)

        self.navbar.setStyleSheet("""
    QToolBar {
        background-color: #f0f0f0;
        border: none;
        padding: 5px;
    }
    QToolButton {
        background-color: #fff;
        border: 1px solid #ddd;
        padding: 5px;
        margin: 2px;
        border-radius: 5px;
        box-shadow: 0px 0px 5px rgba(0,0,0,0.1);
        transition: background-color 0.3s ease, box-shadow 0.3s ease;
    }
    QToolButton:hover {
        background-color: #e0e0e0;
        border: 1px solid #ccc;
        box-shadow: 0px 0px 10px rgba(0,0,0,0.2);
    }
    QToolButton:pressed {
        background-color: #d0d0d0;
        border: 1px solid #bbb;
        box-shadow: 0px 0px 5px rgba(0,0,0,0.1);
        transform: translateY(2px);
    }
             """)

        back_btn = QAction('Back', self)
        back_btn.triggered.connect(self.browser.back)
        self.navbar.addAction(back_btn)

        forward_btn = QAction('Forward', self)
        forward_btn.triggered.connect(self.browser.forward)
        self.navbar.addAction(forward_btn)

        reload_btn = QAction('Reload', self)
        reload_btn.triggered.connect(self.browser.reload)
        self.navbar.addAction(reload_btn)

        home_btn = QAction('Home', self)
        home_btn.triggered.connect(self.navigate_home)
        self.navbar.addAction(home_btn)

        self.url_bar = QLineEdit()
        self.url_bar.returnPressed.connect(self.navigate_to_url)
        self.navbar.addWidget(self.url_bar)

        self.browser.urlChanged.connect(self.update_url)

        search_engines = ['Google', 'Bing', 'DuckDuckGo']
        self.search_engine_selector = QComboBox()
        self.search_engine_selector.addItems(search_engines)
        self.search_engine_selector.currentTextChanged.connect(self.update_url_bar)
        self.search_engine_selector.currentTextChanged.connect(self.update_search_engine_interface)
        self.navbar.addWidget(self.search_engine_selector)

        bookmarks_btn = QAction('Bookmarks', self)
        bookmarks_btn.triggered.connect(self.show_bookmarks)
        self.navbar.addAction(bookmarks_btn)

        history_btn = QAction('History', self)
        history_btn.triggered.connect(self.show_history)
        self.navbar.addAction(history_btn)

        self.bookmarks = []
        self.history = []

        self.addToolBarBreak()

        self.social_media_toolbar = QToolBar()
        self.addToolBar(self.social_media_toolbar)
        youtube_btn = QAction('Youtube', self)
        youtube_btn.triggered.connect(self.open_youtube)
        self.social_media_toolbar.addAction(youtube_btn)
        instagram_btn = QAction('Instagram', self)
        instagram_btn.triggered.connect(self.open_instagram)
        self.social_media_toolbar.addAction(instagram_btn)
        linkedin_btn = QAction('LinkedIn', self)
        linkedin_btn.triggered.connect(self.open_linkedin)
        self.social_media_toolbar.addAction(linkedin_btn)
        facebook_btn = QAction('Facebook', self)
        facebook_btn.triggered.connect(self.open_facebook)
        self.social_media_toolbar.addAction(facebook_btn)
        twitter_btn = QAction('Twitter', self)
        twitter_btn.triggered.connect(self.open_twitter)
        self.social_media_toolbar.addAction(twitter_btn)

        self.virtual_mouse_button = QToolButton()
        self.virtual_mouse_button.setText("Virtual Mouse")
        self.virtual_mouse_button.setPopupMode(QToolButton.InstantPopup)
        self.social_media_toolbar.addWidget(self.virtual_mouse_button)

        self.virtual_mouse_menu = QMenu()
        self.virtual_mouse_button.setMenu(self.virtual_mouse_menu)

        self.start_virtual_mouse_action = QAction("Start", self)
        self.start_virtual_mouse_action.triggered.connect(runvirtualmouse)
        self.virtual_mouse_menu.addAction(self.start_virtual_mouse_action)

        self.stop_virtual_mouse_action = QAction("Stop", self)
        self.stop_virtual_mouse_action.triggered.connect(stopvirtualmouse)
        self.virtual_mouse_menu.addAction(self.stop_virtual_mouse_action)

        username_btn = QPushButton()
        username_btn.setFlat(True)
        self.social_media_toolbar.addWidget(username_btn)

    def close_event(self, event):
        if self.closing_bookmarks_or_history:
            event.ignore()
            self.closing_bookmarks_or_history = False
        else:
            self.parent.save_data()
            event.accept()

    def save_history(self, username, history):
        filename = f"{username}_history.json"
        with open(filename, 'w') as f:
            json.dump(history, f)

    def add_history(self, url):
        if self.username in self.user_history:
            self.user_history[self.username].append(url)
        else:
            self.user_history[self.username] = [url]
        self.parent.save_history(self.username, self.user_history[self.username])

    def save_bookmarks(self, username, bookmarks):
        file_path = f'{username}_bookmarks.json'
        if not os.path.exists(file_path):
            data = {}
        else:
            with open(file_path, 'r') as f:
                try:
                    data = json.load(f)
                    if not isinstance(data, dict):
                        data = {}
                except (ValueError, FileNotFoundError):
                    data = {}
    
        data[username] = bookmarks
        with open(file_path, 'w') as f:
            try:
                json.dump(data, f)
            except Exception as e:
                print(f"Error saving bookmarks: {e}")

    def show_user_account(self, username):
        self.username = username
        self.username_btn = QPushButton(username)
        self.username_btn.setFlat(True)
        self.username_menu = QMenu()
        self.logout_action = QAction('Logout')
        self.logout_action.triggered.connect(self.logout)
        self.username_menu.addAction(self.logout_action)
        self.username_btn.setMenu(self.username_menu)
        self.social_media_toolbar.addWidget(self.username_btn)

    def logout(self):
        self.username_btn.deleteLater()
        self.parent.show_login_window()

    def open_youtube(self):
        self.browser.setUrl(QUrl('https://m.youtube.com'))

    def open_instagram(self):
        self.browser.setUrl(QUrl('https://www.instagram.com'))

    def open_linkedin(self):
        self.browser.setUrl(QUrl('https://www.linkedin.com'))

    def open_facebook(self):
        self.browser.setUrl(QUrl('https://www.facebook.com'))

    def open_twitter(self):
        self.browser.setUrl(QUrl('https://www.twitter.com'))

    def navigate_home(self):
        current_search_engine = self.search_engine_selector.currentText()
        if current_search_engine == 'Google':
            self.browser.setUrl(QUrl('https://www.google.com'))
        elif current_search_engine == 'Bing':
            self.browser.setUrl(QUrl('https://www.bing.com'))
        elif current_search_engine == 'DuckDuckGo':
            self.browser.setUrl(QUrl('https://duckduckgo.com'))

    def navigate_to_url(self):
        url = self.url_bar.text()
        search_engine = self.search_engine_selector.currentText()
        if search_engine == 'Google':
            url = 'https://www.google.com/search?q=' + url
        elif search_engine == 'Bing':
            url = 'https://www.bing.com/search?q=' + url
        elif search_engine == 'DuckDuckGo':
            url = 'https://duckduckgo.com/?q=' + url
        self.browser.setUrl(QUrl(url))

    def update_url(self, q):
        url = q.toString()
        if url != self.last_url and url.rstrip('/') != self.last_url:
            self.history.append(url)
            self.save_history(self.username, self.history)
            self.last_url = url
            self.url_bar.setText(url)

    def update_url_bar(self, text):
        url = self.url_bar.text()
        if text == 'Google':
            self.url_bar.setText('https://www.google.com/search?q=')
        elif text == 'Bing':
            self.url_bar.setText('https://www.bing.com/search?q=')
        elif text == 'DuckDuckGo':
            self.url_bar.setText('https://duckduckgo.com/?q=')

    def show_history(self):
        self.history = self.parent.load_history(self.username)

        if not hasattr(self, 'history_window') or not self.history_window.isVisible():
            self.history_window = QDialog()
            self.history_window.setWindowTitle('History')

            self.history_list = QListWidget()
            history_layout = QVBoxLayout()
            history_layout.addWidget(self.history_list)

            clear_history_btn = QPushButton('Clear History')
            clear_history_btn.clicked.connect(self.clear_history)
            history_layout.addWidget(clear_history_btn)

            delete_all_history_btn = QPushButton('Clear All History')
            delete_all_history_btn.clicked.connect(lambda:self.clear_all_history())
            history_layout.addWidget(delete_all_history_btn)

            self.history_window.setLayout(history_layout)
            self.history_window.setMinimumSize(400, 300)
            self.history_window.closeEvent = self.history_window_close_event
        self.history = self.parent.load_history(self.username)
        print(self.history)
        self.history_list.clear()
        if self.history:
            self.history_list.addItems(self.history)
        else:
            self.history_list.addItem("No history")
        self.history_window.show()


    def history_window_close_event(self, event):
        self.closing_bookmarks_or_history = True
        event.accept()

    def bookmarks_window_close_event(self, event):
        self.closing_bookmarks_or_history = True
        event.accept()

    def show_bookmarks(self):
        if not hasattr(self, 'bookmarks_window') or not self.bookmarks_window.isVisible():
            self.bookmarks_window = QDialog()
            self.bookmarks_window.setWindowTitle('Bookmarks')
            self.bookmarks_list = QListWidget()
            self.bookmarks_window_layout = QVBoxLayout()
            self.bookmarks_window_layout.addWidget(self.bookmarks_list)
            add_bookmark_btn = QPushButton('Add Bookmark')
            add_bookmark_btn.clicked.connect(self.add_bookmark)
            self.bookmarks_window_layout.addWidget(add_bookmark_btn)
            delete_bookmark_btn = QPushButton('Delete Bookmark')
            delete_bookmark_btn.clicked.connect(self.delete_bookmark)
            self.bookmarks_window_layout.addWidget(delete_bookmark_btn)
            self.bookmarks_window.setLayout(self.bookmarks_window_layout)
            self.bookmarks_window.setMinimumSize(400, 300)
            self.bookmarks_window.closeEvent = self.bookmarks_window_close_event
        self.bookmarks = self.parent.load_bookmarks(self.username)
        self.bookmarks_list.clear()
        if self.bookmarks:
            self.bookmarks_list.addItems([f"{bm['title']} - {bm['url']}" for bm in self.bookmarks])
        else:
            self.bookmarks_list.addItem("No bookmarks")
        self.bookmarks_window.show()

    def add_bookmark(self):
        current_url = self.browser.url().toString()
        bookmark_title = self.browser.page().title()
    
        bookmarks = self.parent.load_bookmarks(self.username)
        if not any(bm["url"] == current_url for bm in bookmarks):
            bookmarks.append({"title": bookmark_title, "url": current_url})
            self.save_bookmarks(self.username, bookmarks)
            self.show_bookmarks()
            print(f"Bookmark added: {bookmark_title} - {current_url}")
        else:
            print("Bookmark alreadyÂ exists")

    def clear_history(self):
        selected_items = [item.text() for item in self.history_list.selectedItems()]
        for item in selected_items:
            self.history.remove(item)
        self.save_history(self.username, self.history)
        self.history_list.clear()
        self.history_list.addItems(self.history)
        if hasattr(self, 'history_window'):
            self.history_window.close()
        self.show_history()
    
    def clear_all_history(self):
        print("Delete all history button clicked")
        confirm_delete = QMessageBox.question(self, "Delete all History", "Are you sure?")
        print(f"Confirm delete response: {confirm_delete}")
    
        if confirm_delete == QMessageBox.Yes:
            print("Deleting history...")
            self.parent.save_history(self.username, [])
            self.history_list.clear()
            self.update_history_list()

    def update_history_list(self):
        for item in self.parent.history:
            self.history_list.addItem(item)
        if not self.history:
            self.history_list.addItem("No History")
            
    def delete_bookmark(self):
        try:
            selected_indexes = [item.row() for item in self.bookmarks_list.selectedItems()]
        
            for index in sorted(selected_indexes, reverse=True):
                del self.bookmarks[index]
        
            self.save_bookmarks(self.username, self.bookmarks)
        
            self.bookmarks_list.clear()
            self.bookmarks_list.addItems([bm["title"] for bm in self.bookmarks])
        
            if not self.bookmarks:
                self.bookmarks_list.addItem("No bookmarks")
    
        except Exception as e:
            print(f"Error deleting bookmark: {e}")

    def update_search_engine_interface(self, text):
        if text == 'Google':
            self.browser.setUrl(QUrl('https://www.google.com'))
        elif text == 'Bing':
            self.browser.setUrl(QUrl('https://www.bing.com'))
        elif text == 'DuckDuckGo':
            self.browser.setUrl(QUrl('https://duckduckgo.com'))


def load_json(filename):
        try:
            with open(filename, 'r') as file:
                return json.load(file)
        except FileNotFoundError:
            return {}
        except json.JSONDecodeError as e:
            print(f"Error parsing JSON: {e}")
            return {}


class LoginWindow(QWidget):
    def __init__(self, parent):
        super(LoginWindow, self).__init__()
        self.parent = parent
        self.users={}
        self.data={}
        
        layout = QVBoxLayout()
    
        self.header_widget = QWidget()
        self.header_layout = QHBoxLayout()
        self.header_widget.setLayout(self.header_layout)

        self.username_input = QLineEdit()
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)

        self.show_password_checkbox = QCheckBox('Show Password')
        self.show_password_checkbox.stateChanged.connect(self.show_password)

        self.error_label = QLabel()

        forgot_password_btn = QPushButton("Forgot Password")
        forgot_password_btn.clicked.connect(self.show_forgot_password_window)

        layout.addWidget(QLabel("Username"))
        layout.addWidget(self.username_input)
        layout.addWidget(QLabel("Password"))
        layout.addWidget(self.password_input)
        layout.addWidget(self.show_password_checkbox)
        layout.addWidget(self.error_label)
        layout.addWidget(forgot_password_btn)

        login_btn = QPushButton("Login")
        login_btn.clicked.connect(self.login) 

        register_btn = QPushButton("Register")
        register_btn.clicked.connect(self.show_register_window)

        layout.addWidget(login_btn)
        layout.addWidget(register_btn)

        self.setLayout(layout)

    def login(self):
        username = self.username_input.text().strip()
        password = self.password_input.text().strip()
        try:
            with open('users.json', 'r') as f:
                data = json.load(f)
        except FileNotFoundError:
            print("Error: Users file not found.")
            return
        except json.JSONDecodeError:
            print("Error: Invalid JSON format.")
            return

        if username in data:
            stored_hashed_password = data[username].get("password")
            if stored_hashed_password is None:
                print("Error: Password not found.")
                return

            try:
                if bcrypt.checkpw(password.encode('utf-8'), stored_hashed_password.encode('utf-8')):
                    print("Login successful")
                    self.close()
                    self.browser_window = BrowserWindow(self, username)
                    self.browser_window.show()
                else:
                    print("Incorrect password")
            except Exception as e:
                print(f"Error: {e}")
        else:
            print("Incorrect username")

    def save_data(self):
        try:
            with open('data.json', 'w') as f:
                json.dump(self.data, f)
        except Exception as e:
            print(f"Error saving data: {e}")

    def load_history(self, username):
        try:
            with open(f'{username}_history.json', 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return []
        except json.JSONDecodeError:
            return []

    def load_bookmarks(self, username):
        file_path = f'{username}_bookmarks.json'
        if not os.path.exists(file_path):
            return []
        else:
            with open(file_path, 'r') as f:
                try:
                    data = json.load(f)
                    return data.get(username, [])
                except (ValueError, FileNotFoundError):
                    return []

    def show_password(self, state):
        if state == Qt.Checked:
            self.password_input.setEchoMode(QLineEdit.EchoMode.Normal)
        else:
            self.password_input.setEchoMode(QLineEdit.EchoMode.Password)

    def show_forgot_password_window(self):
        self.forgot_password_window = ForgotPasswordWindow(self)
        self.forgot_password_window.show()
        self.close()

    def show_register_window(self):
        self.parent.right_layout.setCurrentIndex(1)

    def show_login_window(self):
        self.show()
        self.clear_fields()  

    def clear_fields(self):
        self.username_input.clear()
        self.password_input.clear()


class ForgotPasswordWindow(QWidget):bcrypt

def __init__(self, parent):
        super(ForgotPasswordWindow, self).__init__()
        self.parent = parent

        layout = QVBoxLayout()

        self.username_input = QLineEdit()
        self.email_input = QLineEdit()

        send_reset_link_btn = QPushButton("Send Reset Link")
        send_reset_link_btn.clicked.connect(self.send_reset_link)

        layout.addWidget(QLabel("Username"))
        layout.addWidget(self.username_input)
        layout.addWidget(QLabel("Email"))
        layout.addWidget(self.email_input)
        layout.addWidget(send_reset_link_btn)

        self.setLayout(layout)


def send_reset_link(self):
        username = self.username_input.text()
        email = self.email_input.text()

        if username and email:
            reset_token = secrets.token_urlsafe(16)

            reset_link = f"http://example.com/reset-password/{reset_token}"

            print(f"Sending password reset link to {email}: {reset_link}")

            print(f"Storing reset token: {reset_token}")

            QMessageBox.information(self, "Password Reset", "Password reset link sent successfully!")
        else:
            QMessageBox.warning(self, "Password Reset", "Invalid username or email")

        sender_email = "your_sender_email@example.com"
        recipient_email = email
        email_subject = "Password Reset Link"
        email_body = f"Reset link: {reset_link}"

        msg = MIMEText(email_body)
        msg['Subject'] = email_subject
        msg['From'] = sender_email
        msg['To'] = recipient_email

        try:
            server = smtplib.SMTP('smtp.example.com', 587)
            server.starttls()
            server.login(sender_email, "your_sender_password")
            server.sendmail(sender_email, recipient_email, msg.as_string())
            server.quit()
        except socket.gaierror as e:

            print(f"Socket error: {e}")


class VerifyEmailWindow(QWidget):
    def __init__(self, parent=None, **kwargs):
        super(VerifyEmailWindow, self).__init__(parent)
        self.username = kwargs.get('username', "")
        self.parent = parent
        layout = QVBoxLayout()
        
        self.verification_code_input = QLineEdit()
        layout.addWidget(QLabel("Verification Code"))
        layout.addWidget(self.verification_code_input)
        
        verify_btn = QPushButton("Verify")
        verify_btn.clicked.connect(self.verify_email)
        
        layout.addWidget(verify_btn)
        
        self.setLayout(layout)
        
    def verify_email(self):
        verification_code = self.verification_code_input.text()
        
        if self.parent.users[self.username]['verification_code'] == verification_code:
            self.parent.users[self.username]['verified'] = True
            print("Email verified")
            # Show login window
            self.parent.show_login_window()
            self.close()
        else:
            print("Invalid verification code")


class RegisterWindow(QWidget):
    def __init__(self, parent):
        super(RegisterWindow, self).__init__()
        self.parent = parent
        layout = QVBoxLayout()
        
        self.username_input = QLineEdit()
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)
        self.email_input = QLineEdit()
        self.confirm_password_input = QLineEdit()
        self.confirm_password_input.setEchoMode(QLineEdit.Password)
        
        layout.addWidget(QLabel("Username"))
        layout.addWidget(self.username_input)
        layout.addWidget(QLabel("Email"))
        layout.addWidget(self.email_input)
        layout.addWidget(QLabel("Password"))
        layout.addWidget(self.password_input)
        layout.addWidget(QLabel("Confirm Password"))
        layout.addWidget(self.confirm_password_input)
        
        register_btn = QPushButton("Register")
        register_btn.clicked.connect(self.register)
        loginbtn = QPushButton("Back")
        loginbtn.clicked.connect(self.login)
        
        layout.addWidget(register_btn)
        layout.addWidget(loginbtn)
        
        self.setLayout(layout)

    def login(self):
        self.parent.right_layout.setCurrentIndex(0)
        self.close()

    def register(self):
        username = self.username_input.text()
        email = self.email_input.text()
        password = self.password_input.text()
        confirm_password = self.confirm_password_input.text()
        
        if password != confirm_password:
            print("Passwords do not match")
            return
        
        import re
        email_regex = r"[^@]+@[^@]+\.[^@]+"
        if not re.match(email_regex, email):
            print("Invalid email")
            return
        
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        
        verification_code = str(random.randint(100000, 999999))

        filename = 'users.json'
        if not os.path.exists(filename):
            with open(filename, 'w') as file:
                json.dump({}, file)
    
        with open(filename, 'r+') as file:
            data = json.load(file)
        data[username] = {
            'password': hashed_password,
            'email': email,
            'verification_code': verification_code,
            'verified': False
        }
        with open(filename, 'w') as file:
            json.dump(data, file)
        
        print("Registration successful")
        self.parent.right_layout.setCurrentIndex(0)
        self.close()
        self.verify_email_window = VerifyEmailWindow(self.parent, username=username)
        self.verify_email_window.show()

    def send_verification_email(self, email, verification_code):
        msg = EmailMessage()
        msg.set_content(f"Verification code: {verification_code}")
        msg['Subject'] = "Email Verification"
        msg['From'] = "ananonymousa12@gmail.com"
        msg['To'] = email
    
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
            smtp.login("ananonymousa12@gmail.com", "Shiva@130")
            smtp.send_message(msg)

    def show_password(self):
        if self.show_password_checkbox.isChecked():
            self.password_input.setEchoMode(QLineEdit.EchoMode.Normal)
            self.confirm_password_input.setEchoMode(QLineEdit.EchoMode.Normal)
        else:
            self.password_input.setEchoMode(QLineEdit.Password)
            self.confirm_password_input.setEchoMode(QLineEdit.Password)


def update_url_bar(self, text):
    url = self.url_bar.text()
    if text == 'Google':
        self.url_bar.setText('https://www.google.com/search?q=')
        self.default_search_engine = 'Google'
    elif text == 'Bing':
        self.url_bar.setText('https://www.bing.com/search?q=')
        self.default_search_engine = 'Bing'
    elif text == 'DuckDuckGo':
        self.url_bar.setText('https://duckduckgo.com/?q=')
        self.default_search_engine = 'DuckDuckGo'


def navigate_to_url(self):
    url = self.url_bar.text()
    if self.default_search_engine == 'Google':
        url = 'https://www.google.com/search?q=' + url
    elif self.default_search_engine == 'Bing':
        url = 'https://www.bing.com/search?q=' + url
    elif self.default_search_engine == 'DuckDuckGo':
        url = 'https://duckduckgo.com/?q=' + url
    self.browser.setUrl(QUrl(url))


app = QApplication(sys.argv)
QApplication.setApplicationName('Q-Search')
window = MainWindow()


def save_data(self):
    if hasattr(self.browser_window, 'username') and self.browser_window.username is not None:
        bookmarks = self.browser_window.load_bookmarks(self.browser_window.username)
        self.browser_window.save_bookmarks(self.browser_window.username, bookmarks)


sys.exit(app.exec_())