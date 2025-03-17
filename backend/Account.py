import json

# Function to control logging into the system.
def login():
    try:
        with open('very secure credentials folder\\credentials.json', 'r') as fp:
            credentials = json.load(fp)  # Load list of user dictionaries
    except (FileNotFoundError, json.JSONDecodeError):
        print("No account found. Please sign up first.")
        return

    enteredusername = input("Enter Username:\n")
    enteredpassword = input("Enter Password:\n")

    # Search for a matching username and password
    for account in credentials:
        if account["username"] == enteredusername and account["password"] == enteredpassword:
            print("Login successful!")
            return Account(enteredusername, enteredpassword)  # Create and return an account object
        
    print("Invalid username or password.") 

class Account:
    # Creates a new account object with a username and password
    def __init__(self, username, password):
        self.username = username
        self.password = password

    # Prints out the username and password of the account
    def __str__(self):
        return f"Username: {self.username}\nPassword: {self.password}"

    # Allows user to change their username
    def edit_username(self):
        self.username = input("What do you want to change the username to?\n")
        print("Username changed to " + self.username)

    # Allows user to change their password
    def edit_password(self):
        self.password = input("What do you want to change the password to?\n")
        print("Password changed successfully.")

    # Allows user to interact with settings
    def settingscarousel(self):
        while True:
            print("\nWelcome " + self.username + "! Select a number: \n")
            print("1. Check Account Details\n2. Change Username\n3. Change Password\n4. Exit.")

            try:
                option = int(input("What do you want to do?\n"))
            except ValueError:
                print("Invalid input. Please enter a number between 1 and 4.")
                continue

            if option == 1:
                print(self)
            elif option == 2:
                self.edit_username()
            elif option == 3:
                self.edit_password()
            elif option == 4:
                print("Exiting settings...")
                break
            else:
                print("Invalid option. Please try again.")

# Attempt login
useraccount = login()

# If login was successful, allow access to settings
if useraccount:
    useraccount.settingscarousel()


    