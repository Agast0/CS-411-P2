import json
from authentication_module.utils.hash_utils import verify_password
from flask import session

class AuthenticationService:
    def __init__(self):
        self.users_data_file = 'authentication_module/models/data/users.json'

    def load_users(self):
        with open(self.users_data_file, 'r') as file:
            return json.load(file)

    def login(self, username, password):
        users = self.load_users()
        for user in users:
            if user['username'] == username and verify_password(password, user['password']):
                return {"authenticated": True, "role": user.get("role")}  # Return both authentication status and role
        return {"authenticated": False, "role": None}  # Return a default structure when authentication fails

    def is_authenticated(self):
        return {
            "authenticated": session.get('user_authenticated'),
            "role": session.get('user_role')
        }