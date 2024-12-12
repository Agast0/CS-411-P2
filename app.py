from flask import Flask
from authentication_module.routes import auth_bp
import secrets  # Import secrets to generate a secure secret key

from authentication_module.utils.hash_utils import hash_password
from inpatient_module.routes import inpatient_bp
from patient_admission_module.routes import admission_bp

app = Flask(__name__)

# Set a secret key for the session management
app.secret_key = secrets.token_urlsafe(16)

# Register the authentication blueprint
app.register_blueprint(auth_bp)
app.register_blueprint(admission_bp)
app.register_blueprint(inpatient_bp)

if __name__ == '__main__':
    app.run(debug=True)
