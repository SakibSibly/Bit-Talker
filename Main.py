from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5 import uic
from btmodules import Account, Notification
from client.Client import Client
import hashlib
import threading
import time
from datetime import datetime
import pytz


connection = Client()
thread_life = True  # For controlling the thread in realtime


def dark():
	widgets.setStyleSheet("background-color: #333;color: white;")


def light():
	widgets.setStyleSheet("")


# Month substitution dictionary
months_shortcuts = {
	'01': 'Jan',
	'02': 'Feb',
	'03': 'Mar',
	'04': 'Apr',
	'05': 'May',
	'06': 'Jun',
	'07': 'Jul',
	'08': 'Aug',
	'09': 'Sep',
	'10': 'Oct',
	'11': 'Nov',
	'12': 'Dec'
}


class LoginForm(QMainWindow):
	def __init__(self):
		super(LoginForm, self).__init__()
		uic.loadUi("ui/login_form.ui", self)

		self.login_button.clicked.connect(self.login)
		self.signup_button.clicked.connect(lambda: widgets.setCurrentIndex(1))
		self.actionDarkMode.triggered.connect(dark)
		self.actionLightMode.triggered.connect(light)
		self.actionQuit.triggered.connect(exit)
		self.bt_image.setStyleSheet("image : url(pictures/main_icon.png) no-repeat center;")
		self.show()

	def login(self):
		
		email = str(self.email_field.text()).lower().strip()
		password = hashlib.sha256(str(self.password_field.text()).encode()).hexdigest()

		msg = Account.valid_login(email, password)

		if msg != "Successfully logged in":
			QMessageBox().warning(self, "Login Failed", msg, QMessageBox.Ok)
		else:
			global senderID
			senderID = connection.sendQuery("get_id_by_email", [email])

			# Handling the post logout phase of showing the previous user's messages
			try:
				global receiverID
				receiverID = [(-1,)]
			except Exception as e:
				print(f"[PROBLEM in login] {e}")

			self.email_field.clear()
			self.password_field.clear()
			self.email_field.setFocus()

			global thread_life
			thread_life = True

			window3 = MainChatWindow()
			widgets.addWidget(window3)
			widgets.setCurrentIndex(2)


class CreateAccount(QMainWindow):

	def __init__(self):
		super(CreateAccount, self).__init__()
		uic.loadUi("ui/create_account.ui", self)

		self.create_and_login_button.clicked.connect(self.createAccount)
		self.cancel_button.clicked.connect(lambda: widgets.setCurrentIndex(0))
		self.actionQuit.triggered.connect(exit)
		self.actionDarkMode_2.triggered.connect(dark)
		self.actionLightMode_2.triggered.connect(light)
		
		self.show()

	def createAccount(self):
		initial_length = len(str(self.password_field.text()))
		name = str(self.name_field.text()).strip()
		username = str(self.username_field.text()).strip()
		email = str(self.email_field.text()).strip()
		password = hashlib.sha256(str(self.password_field.text()).encode()).hexdigest()
		re_password = hashlib.sha256(str(self.password_field_2.text()).encode()).hexdigest()

		confirmation = Account.validate(name, username, email, password, re_password, initial_length)

		if confirmation == "Shob E Maya":
			widgets.setCurrentIndex(0)
			QMessageBox().information(self, "Status", Account.create(name, username, email, password), QMessageBox.Ok)
		else:
			QMessageBox().warning(self, "Invalid Credential", confirmation,QMessageBox.Ok)


class MainChatWindow(QMainWindow):
	def __init__(self):
		super(MainChatWindow, self).__init__()
		uic.loadUi("ui/chatting_window.ui", self)

		self.buttons_list = {}

		self.search_bar.textChanged.connect(lambda: self.searchList(self.search_bar.text()))

		self.v_spacer = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)
		self.userList_layout = QVBoxLayout(self.user_list)
		self.userList()

		message_lookup = threading.Thread(target=self.updateWindow)
		message_lookup.start()

		self.send_button.clicked.connect(self.send)

		self.actionProfile.triggered.connect(self.gotoProfile)
		self.actionDarkMode_3.triggered.connect(dark)
		self.actionLightMode_3.triggered.connect(light)
		self.actionDelete.triggered.connect(self.gotoAccountDeletion)
		self.actionExit.triggered.connect(self.terminate)
		self.actionLogout.triggered.connect(self.logout)

		self.show()

	def gotoAccountDeletion(self):
		window4 = DeleteAccount()
		widgets.addWidget(window4)
		widgets.setCurrentIndex(3)

	def terminate(self):
		global thread_life
		thread_life = False
		exit()

	def gotoProfile(self):
		win = uic.loadUi("ui/profile.ui")
		win.profile_photo.setStyleSheet("background : url(pictures/user.png) no-repeat center;")
		
		user_info = connection.sendQuery("get_all_by_id", [senderID[0][0]])

		win.profile_name.setText(user_info[0][1])
		win.profile_username.setText(user_info[0][2])
		win.profile_email.setText(user_info[0][3])
		win.profile_id.setText(str(user_info[0][0]))
		win.setWindowTitle("BitTalker")
		win.setWindowIcon(QIcon("pictures/main_icon.png"))
		win.exec_()

	def logout(self):
		global thread_life
		thread_life = False
		wid = widgets.widget(2)
		widgets.removeWidget(wid)
		wid.deleteLater()
		widgets.setCurrentIndex(0)

	def userList(self):

		names = connection.sendQuery("fetch_user", [senderID[0][0]])

		for username in names:
			user = uic.loadUi("ui//user.ui")
			parts = user.findChildren(QPushButton)

			img = parts[0]
			img.setStyleSheet("background : url(pictures/user.png) no-repeat center;")
			
			username_field = parts[1]
			username_field.setText(username[1])

			username_field.setCheckable(True)
			username_field.setChecked(False)
			self.buttons_list[username_field] = username_field.isChecked()

			username_field.clicked.connect(lambda clicked, name=username, btn=username_field: self.showChats(name, btn))

			self.userList_layout.addWidget(user)

		self.userList_layout.addItem(self.v_spacer)

	def searchList(self, target_name):

		for widget in self.user_list.findChildren(QWidget):
			widget.deleteLater()

		self.userList_layout.removeItem(self.v_spacer)

		names = connection.sendQuery("fetch_user_search", [target_name, senderID[0][0]])

		for username in names:
			user = uic.loadUi("ui//user.ui")
			parts = user.findChildren(QPushButton)

			img = parts[0]
			img.setStyleSheet("background : url(pictures/user.png) no-repeat center;")
			
			u_name = parts[1]
			u_name.setText(username[1])

			u_name.setCheckable(True)
			u_name.setChecked(False)
			self.buttons_list[u_name] = u_name.isChecked()
			u_name.clicked.connect(lambda clicked, name=username, btn=u_name: self.showChats(name, btn))
			self.userList_layout.addWidget(user)

		self.userList_layout.addItem(self.v_spacer)

	def send(self):
		if self.message_field.text():
			dhaka_timezone = pytz.timezone('Asia/Dhaka')
			current_time = datetime.now(dhaka_timezone)
			filtered_time = current_time.strftime('%h %d  %I:%M %p')

			text = self.message_field.text() + "\n" + filtered_time
			item = QListWidgetItem(text)
			item.setTextAlignment(Qt.AlignRight)

			# Check if the receiver is selected or not
			if receiverID[0][0] != -1:
				try:
					connection.sendQuery("update_chats", [senderID[0][0], receiverID[0][0], self.message_field.text()])
					self.messages.addItem(item)
					self.message_field.clear()

				except Exception as e:
					self.message_field.clear()
					print(f"[PROBLEM in send] {e}")
			else:
				self.message_field.clear()

	def withTime(self, msg):
		text = msg[1]
		filtered_time = str(msg[2]).split(":")
		filtered_date = str(msg[3]).split('-')
		day = filtered_date[2]
		month = months_shortcuts[filtered_date[1]]

		if (12 - int(filtered_time[0])) == 0:  # 12:10
			result = "12:" + filtered_time[1] + " PM"
		elif (12 - int(filtered_time[0])) == 12:  # 00:10
			result = "12:" + filtered_time[1] + " AM"
		elif (12 - int(filtered_time[0])) > 0:  # 13:10
			result = filtered_time[0] + ":" + filtered_time[1] + " AM"
		else:  # 10:10
			result = str(int(filtered_time[0]) - 12) + ":" + filtered_time[1] + " PM"
				
		text += "\n" + month + " " + day + "  " + result
		return text

	def showChats(self, name_of_user, button):
		
		if self.buttons_list[button]:
			return

		for key in self.buttons_list:
			self.buttons_list[key] = False

		button.setCheckable(True)
		button.setChecked(True)

		self.buttons_list[button] = True

		self.user_name.setText(name_of_user[0])
		self.user_photo.setStyleSheet("background : url(pictures/user.png) no-repeat center;")

		global receiverID
		receiverID = connection.sendQuery("get_id_by_username", [name_of_user[0]])
		chats = connection.sendQuery("showMessages", [senderID[0][0], receiverID[0][0]])

		self.messages.clear()

		if chats:
			for msg in chats:
				text = self.withTime(msg)
				item = QListWidgetItem(text)

				if msg[0] == senderID[0][0]:
					item.setTextAlignment(Qt.AlignRight)

				self.messages.addItem(item)
				connection.sendQuery("message_taken", [receiverID[0][0], senderID[0][0]])
				connection.sendQuery("message_taken", [senderID[0][0], receiverID[0][0]])
				connection.sendQuery("message_notified", [senderID[0][0]])
	
	def updateWindow(self):
		global thread_life

		while thread_life:
			try:
				time.sleep(3)
				msg = connection.sendQuery("look_for_message", [receiverID[0][0], senderID[0][0]])
				if msg:
					for messages in msg:
						text = self.withTime(messages)
						self.messages.addItem(text)
						connection.sendQuery("message_taken", [receiverID[0][0], senderID[0][0]])

			except Exception as e:
				print(f"[PROBLEM in updateWindow] {e}")

			finally:
				# Notification Feature
				confirmation = connection.sendQuery("look_for_any_incoming_message", [senderID[0][0]])
				if confirmation:
					for row in confirmation:
						retrieved_name = connection.sendQuery('get_all_by_id', [row[0]])[0][1]
						Notification.createNotification(f"New Message from {retrieved_name}", row[1])
						connection.sendQuery("message_notified", [senderID[0][0]])


class DeleteAccount(QMainWindow):
	def __init__(self):
		super(DeleteAccount, self).__init__()
		uic.loadUi("ui/delete_account.ui", self)

		self.bt_image.setStyleSheet("image : url(pictures/main_icon.png) no-repeat center;")
		self.delete_button.clicked.connect(self.deleteUser)
		self.cancel_button.clicked.connect(self.backToMainChatWindow)
		self.actionDarkMode_4.triggered.connect(dark)
		self.actionLightMode_4.triggered.connect(light)
		self.actionQuit.triggered.connect(self.terminate)

		self.show()

	def deleteUser(self):
		email = self.email_field.text()
		password = hashlib.sha256(str(self.password_field.text()).encode()).hexdigest()

		user_info = connection.sendQuery("get_all_by_id", [senderID[0][0]])
		user_id = user_info[0][0]
		name = user_info[0][1]
		username = user_info[0][2]

		msg = Account.delete(user_id, name, username, email, password)

		if msg != "Valid":
			QMessageBox().warning(self, "Invalid Credential", msg, QMessageBox.Ok)
		else:
			connection.sendQuery("delete_account", [email])
			global thread_life
			thread_life = False
			wid = widgets.widget(3)
			widgets.removeWidget(wid)
			wid.deleteLater()

			wid = widgets.widget(2)
			widgets.removeWidget(wid)
			wid.deleteLater()
			widgets.setCurrentIndex(0)
			QMessageBox().warning(self, "Account update", "Account Successfully Deleted!", QMessageBox.Ok)

	def backToMainChatWindow(self):
		wid = widgets.widget(3)
		widgets.removeWidget(wid)
		wid.deleteLater()
		widgets.setCurrentIndex(2)

	def terminate(self):
		global thread_life
		thread_life = False
		exit()

def main():
	app = QApplication([])

	global widgets
	widgets = QStackedWidget()
	widgets.setWindowTitle("BitTalker")
	widgets.setWindowIcon(QIcon("pictures/main_icon.png"))

	window1 = LoginForm()
	widgets.addWidget(window1)

	window2 = CreateAccount()
	widgets.addWidget(window2)

	widgets.show()
	app.exec_()


if __name__ == "__main__":
	main()
