from email_validator import validate_email,EmailNotValidError
from client.Client import Client
connection = Client()


def ok(email):
	try:
		validate_email(email)
		return True
	except EmailNotValidError:
		return False
	

def validate(name,username,email,password,re_password,initial_length):
	if not name or not username or not email or not password or not re_password:
		return "One of the required field(s) is missing!"

	elif not ok(email):
		return "Invalid Email!"

	elif password != re_password:
		return "Re-typed passwords didn't match with the previous one!"

	elif initial_length < 8:
		return "Too small password!"

	dbase = connection.send_query("database_check", [username,email])
	print(dbase)
 
	if not len(dbase):
		return "Shob E Maya"
	elif dbase[0][0] == username:
		return "Username isn't available!"
	else:
		return "Email is already regestered!"
	
		

def create(name,username,email,password):
	result = connection.send_query("database_check", [username,email])
	
	if result:
		return f'"{email}" is already used by another user!'
	else:
		connection.send_query("create_account", [name,username,email,password])
		return "Account created successfully"


def valid_login(email, password):
	result = connection.send_query("valid_login", [email,password])
	# print(result)
 
	if result[0][0]:
		return "Successfully logged in"
	else:
		return "Invalid login Credential"

def search():
	pass

def delete():
	pass
