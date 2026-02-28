from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from datetime import datetime, timedelta
import bcrypt
import os
import json
from dotenv import load_dotenv

print("🚀 Starting app.py...")

load_dotenv()

app = Flask(__name__)
print("✅ Flask app created")

CORS(app)
print("✅ CORS enabled")

# Configuration
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'your-secret-key-change-this')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///mental_health.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'jwt-secret-key-change-this')
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(days=1)

print("✅ Configuration set")

db = SQLAlchemy(app)
print("✅ Database initialized")

jwt = JWTManager(app)
print("✅ JWT initialized")

# SIMPLE TEST ROUTE - PUT THIS FIRST
@app.route('/')
def home():
    return jsonify({"message": "Main app is running!", "status": "ok"})

@app.route('/test')
def test():
    return jsonify({"message": "Test route works!"})

print("✅ Test routes added")

# ==================== DATABASE MODELS ====================
print("📦 Defining models...")

class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    anonymous_id = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(200))
    role = db.Column(db.String(50))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.anonymous_id,
            'email': self.email,
            'role': self.role,
            'created_at': self.created_at.isoformat()
        }

print("✅ Models defined")

# ==================== AUTHENTICATION ROUTES ====================
print("📦 Adding auth routes...")

@app.route('/api/auth/test', methods=['GET'])
def auth_test():
    return jsonify({"message": "Auth route working"})

@app.route('/api/auth/signup', methods=['POST'])
def signup():
    print("📝 Signup called")
    data = request.json
    email = data.get('email')
    password = data.get('password')
    role = data.get('role', 'student')
    
    # Check if user exists
    if User.query.filter_by(email=email).first():
        return jsonify({'error': 'Email already registered'}), 400
    
    # Hash password
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    
    # Create anonymous ID
    anonymous_id = f"USER_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}"
    
    user = User(
        anonymous_id=anonymous_id,
        email=email,
        password=hashed.decode('utf-8'),
        role=role
    )
    
    db.session.add(user)
    db.session.commit()
    
    # Create access token
    access_token = create_access_token(identity=anonymous_id)
    
    return jsonify({
        'token': access_token,
        'user': user.to_dict()
    }), 201

print("✅ Auth routes added")

# ==================== DEBUG: Print all routes ====================
print("\n" + "="*50)
print("✅ REGISTERED ROUTES:")
for rule in app.url_map.iter_rules():
    print(f"  {rule.endpoint}: {rule.rule}")
print("="*50 + "\n")

# ==================== INIT DATABASE ====================
def init_db():
    with app.app_context():
        db.create_all()
        print("✅ Database tables created!")

# ==================== RUN APP ====================
if __name__ == '__main__':
    init_db()
    print("\n" + "="*50)
    print("🚀 MENTAL WELLNESS PORTAL BACKEND (DEBUG MODE)")
    print("="*50)
    print("📍 Server running at: http://127.0.0.1:5000")
    print("📍 Test routes:")
    print("   • http://127.0.0.1:5000/")
    print("   • http://127.0.0.1:5000/test")
    print("   • http://127.0.0.1:5000/api/auth/test")
    print("="*50 + "\n")
    app.run(debug=True, port=5000)