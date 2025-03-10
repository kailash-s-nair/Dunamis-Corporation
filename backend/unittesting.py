import unittest
from unittest.mock import patch, MagicMock
from flask import json
from app import app, create_access_token


class TestDB(unittest.TestCase):
    #Tests if the database actually connects

    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True

    @patch("app.mysql.connection.cursor")  # Mock DB connection
    def test_db(self, mock_cursor):
        #Tests if database connection is successful
        mock_cursor.return_value.execute.return_value = None
        response = self.app.get('/test_db')
        self.assertEqual(response.status_code, 200)
        self.assertIn("Database connection successful!", response.get_data(as_text=True))


class TestGetUser(unittest.TestCase):
    #Tests fetching user details

    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True

        self.user = {
            "username": "testuser",
            "password": "Test@123",
            "role": "user"
        }
        self.access_token = create_access_token(identity=self.user)

    def test_get_user_success(self):
        #Tests if the system successfully returns the user
        response = self.app.get('/user',
                                headers={"Authorization": f"Bearer {self.access_token}"})

        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data["username"], self.user["username"])
        self.assertEqual(data["role"], self.user["role"])

    def test_get_user_missing_token(self):
        #Tests if the system blocks the attempt with a missing token
        response = self.app.get('/user')

        self.assertEqual(response.status_code, 401)
        self.assertIn("Missing Authorization Header", response.get_data(as_text=True))


class TestRegistration(unittest.TestCase):
    #Tests user registration

    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True

    @patch("app.mysql.connection.cursor") 
    def test_register(self, mock_cursor):
        #Tests a successful user registration
        user = {
            "username": "testuser",
            "password": "Test@123",
            "role": "user"
        }

        response = self.app.post('/register',
                                 data=json.dumps(user),
                                 content_type='application/json')

        self.assertEqual(response.status_code, 200)
        self.assertIn("User registered!", response.get_data(as_text=True))

    def test_register_missing_fields(self):
        #Tests registration failure due to missing fields
        test_user = {
            "username": "testuser"
        }

        response = self.app.post('/register',
                                 data=json.dumps(test_user),
                                 content_type='application/json')

        self.assertEqual(response.status_code, 500)
        self.assertIn("error", response.get_data(as_text=True))

    @patch("app.mysql.connection.cursor")
    def test_register_duplicate_user(self, mock_cursor):
        #Tests for duplicate username registration
        test_user = {
            "username": "testuser",
            "password": "Test@123",
            "role": "user"
        }

        # Simulate existing user in database
        mock_cursor.return_value.execute.side_effect = Exception("Duplicate entry")
        
        response = self.app.post('/register',
                                 data=json.dumps(test_user),
                                 content_type='application/json')

        self.assertEqual(response.status_code, 500)
        self.assertIn("error", response.get_data(as_text=True))


class TestLogin(unittest.TestCase):
    #Tests user login

    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True
        self.admin_user = {
            "username": "adminuser",
            "password": "Admin@123",
            "role": "admin"
        }

    @patch("app.mysql.connection.cursor")
    def test_login(self, mock_cursor):
        #Tests user login and token generation
        mock_cursor.return_value.fetchone.return_value = {
            "id": 1,
            "username": "adminuser",
            "password": "hashedpassword",
            "role": "admin"
        }

        with patch("werkzeug.security.check_password_hash") as mock_check_password:
            mock_check_password.return_value = True 

            response = self.app.post('/login', json={
                "username": self.admin_user['username'],
                "password": self.admin_user['password']
            })

            data = json.loads(response.data)
            self.assertEqual(response.status_code, 200)
            self.assertIn("access_token", data)


if __name__ == '__main__':
    unittest.main()
