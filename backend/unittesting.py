import unittest
from flask import json
from app import app, jwt, sql, create_access_token

class TestDB (unittest.TestCase):

    def setUp(self):
        return super().setUp()
    
    def test_db(self):
        self.assertEqual("Database connection successful!")
    

    
class TestGetUser(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True

        # Create a test user and generate a JWT token
        self.user = {
            "username": "testuser",
            "password": "Test@123",
            "role": "user"
        }
        self.access_token = create_access_token(identity=self.user)  # Generate JWT token

    def test_get_user_success(self):
        response = self.app.get('/user', 
                                headers={"Authorization": f"Bearer {self.access_token}"})
        
        self.assertEqual(response.status_code, 200)  # Ensure request is successful
        data = json.loads(response.data)
        self.assertEqual(data["username"], self.user["username"])  # Check username
        self.assertEqual(data["role"], self.user["role"])  # Check role

    def test_get_user_missing_token(self):
        """Test if the endpoint returns an error when JWT token is missing."""
        response = self.app.get('/user')  # No Authorization header
        
        self.assertEqual(response.status_code, 401)  # Unauthorized access
        self.assertIn("Missing Authorization Header", response.get_data(as_text=True))
        
    



class TestRegistration(unittest.TestCase):
    
    def setUp(self):
        return super().setUp()
    
    #Tests a login attempt. Should be successful with a code and response
    def testRegister(self):
        user = {"username": "testuser",
            "password": "Test@123",
            "role": "user"}
        
        response = self.app.post('/register', 
                                 data=json.dumps(user),
                                 content_type='application/json')

        self.assertEqual(response.status_code, 200)
        self.assertIn("User registered!", response.get_data(as_text=True))

    #Tests for error from missing fields password and role. Should get a status code and response
    def test_register_missing_fields(self):
        """Test registration failure due to missing fields."""
        test_user = {
            "username": "testuser"
            
        }

        response = self.app.post('/register', 
                                 data=json.dumps(test_user),
                                 content_type='application/json')

        self.assertEqual(response.status_code, 500)  
        self.assertIn("error", response.get_data(as_text=True))  

    #Tests for error from duplicate logins. Should return an error code and error response
    def test_register_duplicate_user(self):
        test_user = {
            "username": "testuser",
            "password": "Test@123",
            "role": "user"
        }

        self.app.post('/register', 
                      data=json.dumps(test_user),
                      content_type='application/json')

        response = self.app.post('/register', 
                                 data=json.dumps(test_user),
                                 content_type='application/json')

        self.assertEqual(response.status_code, 500)  # Should return an error for duplicate user
        self.assertIn("error", response.get_data(as_text=True))

        class TestLogin (unittest.TestCase):
            def setUp(self):
                return super().setUp()
            
            