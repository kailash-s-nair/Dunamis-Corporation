# Online Catalogue User Documentation

1. Setup
2. Getting Started
3. FAQ

The online catalogue’s purpose is to store the information of varying objects and information into a web-based database. Items can be added and removed to assist in tracking inventory management, using a server to handle multiple clients and numerous inputs. 


## 1. Setup

To access the database, you must have a device that has a server running. If you are tasked with setting up the server, access this repository:
https://github.com/kailash-s-nair/Dunamis-Corporation

Pull the files to your local device and run the Makefile to obtain all required imports. Make sure to not rename any files and that the file hierarchy is maintained.

Run server.js, located in Frontend/public, in your environment of choice. Should a confirmation message appear, the server is ready to receive inputs.

Access the catalogue through this link:
https://merry-factually-koi.ngrok-free.app/index.html

Ensure that you register for a new username and password, and to give yourself the desired role.


## 2. Getting Started

To login, you will either need to register or have a pre-approved password and username. Registering prompts you for a username, password, your actual name and email address, as well as what role (admin or guest) you require. Guest accounts will have limited access to certain commands.

![image](https://github.com/user-attachments/assets/0feeeee5-d00e-4c8e-9cdd-5eb1b4c5a316)


To add an item, fill in the fields below the categories tab with relevant information. Not all fields need to be filled to add an item. Note that the fields can not contain special characters (“,~,*, etc…). To add a category, select one of the titles in the scrollable list before clicking add item.

![image](https://github.com/user-attachments/assets/5c31f694-f0a3-4e77-9ca4-036a675d378c)


To edit an item, scroll down to the preview of the database. Select an item to be edited and modify the relevant fields. To delete an item, click the delete button of the item you want removed.
To favorite an item, click the star icon of the desired item. The item will appear yellow.

![image](https://github.com/user-attachments/assets/10adb9f8-db41-487e-95c9-dfe0ec63bc10)


To search for an item, search the name of the item. You can include price points, filter by the user who added the item, whether or not the item is in stock, and what category the item is in. Items matching the filtered results will appear below the search criteria form.


![image](https://github.com/user-attachments/assets/c40684db-2d7a-44c4-9044-5b936c6b197b)


Clicking on your name in the top right corner shows your profile settings, including your entered name and email. You can change your password by entering in your current password and entering your new password. To edit your name or change your email, click edit profile. Logging out brings you to the login screen.
![image](https://github.com/user-attachments/assets/0fd56c21-8a7b-49db-912e-cb112a9ff3d4)


## 3. FAQS

**Why is the website not working?**

![image](https://github.com/user-attachments/assets/b79b0fad-d1b3-4111-be03-a3d19787ab7c)

The server is offline. The database must have a running server in order to process usernames and passwords. You may have to request the server to turn back on.

**Why is the database not updating?**
A common cause of this is because the server shuts down partway through entering a product. If the server is running and it is not updating, ensure that the instructions for importing the database are followed

**Why is the item I want not showing up?**
Ensure the item was spelled properly when inputted. Check if you have filters enabled that may hide certain items.
