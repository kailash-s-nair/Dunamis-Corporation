# Online Catalogue Program

# How To Run

Download all files from the repository. You can either pull the files from the repository, or copy each file individually. 
You must make sure that app.py is in the Backend folder, and dashboard.html, index.html, script.js, and style.css are in the Frontend folder.

Open the command line at the directory you downloaded the files into, and run the command **make** to download all python requirements.

![image](https://github.com/user-attachments/assets/37abb2f6-5116-4dea-8740-2247ec3a245f)

Run frontendgui.py. You can run it from a terminal/command line using **python frontendgui.py** or **make run**, open the file in your desired code editor and run from there.

![image](https://github.com/user-attachments/assets/de1ca0f9-4767-4999-b86f-8f81fdb86164)

The program is entirely mouse controlled. Make sure that when adding items they do not include punctuation.

## Setting up and using the MySQL Database

The backend code was designed to use an SQL database. While database parameters are provided,
including a user, password, database id, and hostname/IP, the database can work anywhere with setup,
including locally:

1.  Install MySQL Community Server on your device of choice, setting it as a developer computer. If you want
    If you want to use a user other than root, ensure they have administrative privileges.
2.  Open the MySQL command line interface and type in '__CREATE DATABASE [database name]__.'
3.  Within '__very secure credentials folder/credentials.json__', enter username and password into the
    fields within the brackets.
4.  Through any method (i.e. running the backend.py file), run the command to create the tables or
    format the database.
5.  In '__\_\_init\_\_()__' in the __Database.py__ file, set the database name (in single quotes) 
    to the name of your new database, and the host to either __127.0.0.1__ (if you plan to 
    run it locally), or your device's external IP. If you are using an external device,
    make sure the device is running and accessible via a connection of your choice.

Assuming everything was done correctly, this should create a database with empty tables. The only
tables in this database will be a list of part types, products (all variables by id), 
manufacturers, and a table of products in an intrinsically human-readable form.

Add new part types (i.e. GPU, CPU, fan, etc.) as the need arises. Each part type can have any number of
its own attributes, of either one of two types: a 20-long string of characters, or a whole number.

# Additional Info

The Frontend folder contains the user login and admin privileges.

The Backend folder contains user information and database connections, as well as testing files. You can run the test using pytest in the terminal/command line.