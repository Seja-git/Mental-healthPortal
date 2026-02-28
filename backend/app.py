from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import (
    JWTManager,
    create_access_token,
    jwt_required,
    get_jwt_identity
)
from datetime import datetime, timedelta
import bcrypt
import os
import json
from dotenv import load_dotenv

print("🚀 Starting Mental Wellness Portal Backend...")

load_dotenv()

app = Flask(__name__)
CORS(app)

# ==================== CONFIGURATION ====================

app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'change-this-secret')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///mental_health.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'change-this-jwt-secret')
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(days=1)

db = SQLAlchemy(app)
jwt = JWTManager(app)

# ==================== DATABASE MODELS ====================

class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    anonymous_id = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(50), default="student")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.anonymous_id,
            "email": self.email,
            "role": self.role,
            "created_at": self.created_at.isoformat()
        }

class Appointment(db.Model):
    __tablename__ = 'appointments'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(50), nullable=False)
    counsellor_id = db.Column(db.String(50))
    student_name = db.Column(db.String(100))
    email = db.Column(db.String(100))
    phone = db.Column(db.String(20))
    mode = db.Column(db.String(20))
    counsellor = db.Column(db.String(100))
    date = db.Column(db.String(20))
    time = db.Column(db.String(20))
    duration = db.Column(db.String(20))
    notes = db.Column(db.Text)
    status = db.Column(db.String(20), default='pending')
    meet_link = db.Column(db.String(200))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'student_name': self.student_name,
            'date': self.date,
            'time': self.time,
            'mode': self.mode,
            'counsellor': self.counsellor,
            'status': self.status,
            'meet_link': self.meet_link
        }

class Assessment(db.Model):
    __tablename__ = 'assessments'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(50), nullable=False)
    category = db.Column(db.String(50))
    score = db.Column(db.Integer)
    severity = db.Column(db.String(50))
    responses = db.Column(db.Text)
    date = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'category': self.category,
            'score': self.score,
            'severity': self.severity,
            'date': self.date.isoformat()
        }

class UserActivity(db.Model):
    __tablename__ = 'user_activities'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(50), nullable=False)
    action = db.Column(db.String(200), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

# ==================== BASIC TEST ROUTES ====================

@app.route('/')
def home():
    return jsonify({"message": "Mental Wellness Portal Backend Running"})

@app.route('/test')
def test():
    return jsonify({"message": "Test route working"})

# ==================== AUTH ROUTES ====================

@app.route('/api/auth/signup', methods=['POST'])
def signup():
    data = request.json
    email = data.get('email')
    password = data.get('password')
    role = data.get('role', 'student')

    if not email or not password:
        return jsonify({"error": "Email and password required"}), 400

    if User.query.filter_by(email=email).first():
        return jsonify({"error": "Email already registered"}), 400

    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt)

    anonymous_id = f"USER_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}"

    user = User(
        anonymous_id=anonymous_id,
        email=email,
        password=hashed_password.decode('utf-8'),
        role=role
    )

    db.session.add(user)
    db.session.commit()

    access_token = create_access_token(identity=anonymous_id)

    return jsonify({
        "token": access_token,
        "user": user.to_dict()
    }), 201

@app.route('/api/auth/login', methods=['POST'])
def login():
    data = request.json
    email = data.get('email')
    password = data.get('password')

    user = User.query.filter_by(email=email).first()

    if not user:
        return jsonify({"error": "Invalid credentials"}), 401

    if not bcrypt.checkpw(password.encode('utf-8'), user.password.encode('utf-8')):
        return jsonify({"error": "Invalid credentials"}), 401

    access_token = create_access_token(identity=user.anonymous_id)

    activity = UserActivity(
        user_id=user.anonymous_id,
        action="User logged in"
    )
    db.session.add(activity)
    db.session.commit()

    return jsonify({
        "token": access_token,
        "user": user.to_dict()
    }), 200

# ==================== APPOINTMENT ROUTES ====================

@app.route('/api/counsellors', methods=['GET'])
def get_counsellors():
    counsellors = [
        {"name": "Dr. Asha Patil", "specialization": "Student Stress"},
        {"name": "Dr. Rajesh Sharma", "specialization": "Anxiety & Depression"},
        {"name": "Ms. Sneha Kulkarni", "specialization": "Relationships"},
        {"name": "Mr. Sameer Khan", "specialization": "Career Guidance"}
    ]
    return jsonify(counsellors)

@app.route('/api/appointments', methods=['POST'])
@jwt_required()
def create_appointment():
    user_id = get_jwt_identity()
    data = request.json
    
    meet_link = None
    if data.get('mode') == 'Online (Zoom / Meet)':
        meet_link = f"https://meet.google.com/{os.urandom(4).hex()}"
    
    appointment = Appointment(
        user_id=user_id,
        student_name=data['fullname'],
        email=data['email'],
        phone=data['phone'],
        mode=data['mode'],
        counsellor=data['counsellor'],
        date=data['date'],
        time=data['time'],
        duration=data.get('duration', '30 minutes'),
        notes=data.get('notes', ''),
        meet_link=meet_link
    )
    
    db.session.add(appointment)
    db.session.commit()
    
    return jsonify({
        'id': appointment.id,
        'meet_link': meet_link,
        'status': 'pending'
    }), 201

@app.route('/api/appointments/user', methods=['GET'])
@jwt_required()
def get_user_appointments():
    user_id = get_jwt_identity()
    appointments = Appointment.query.filter_by(user_id=user_id).order_by(Appointment.date).all()
    return jsonify([a.to_dict() for a in appointments])

# ==================== ASSESSMENT ROUTES ====================

@app.route('/api/assessments', methods=['POST'])
@jwt_required()
def save_assessment():
    user_id = get_jwt_identity()
    data = request.json
    
    assessment = Assessment(
        user_id=user_id,
        category=data['category'],
        score=data['score'],
        severity=data['severity'],
        responses=json.dumps(data.get('responses', []))
    )
    
    db.session.add(assessment)
    db.session.commit()
    
    return jsonify(assessment.to_dict()), 201

@app.route('/api/assessments/<user_id>', methods=['GET'])
def get_user_assessments(user_id):
    assessments = Assessment.query.filter_by(user_id=user_id).order_by(Assessment.date.desc()).all()
    return jsonify([a.to_dict() for a in assessments])

# ==================== ADMIN ROUTES ====================

@app.route('/api/admin/users', methods=['GET'])
@jwt_required()
def get_all_users():
    current_user = get_jwt_identity()
    user = User.query.filter_by(anonymous_id=current_user).first()

    if user.role != "organization":
        return jsonify({"error": "Unauthorized"}), 403

    users = User.query.all()
    return jsonify([u.to_dict() for u in users])

@app.route('/api/admin/stats', methods=['GET'])
@jwt_required()
def get_admin_stats():
    current_user = get_jwt_identity()
    user = User.query.filter_by(anonymous_id=current_user).first()

    if user.role != "organization":
        return jsonify({"error": "Unauthorized"}), 403
    
    total_users = User.query.count()
    total_assessments = Assessment.query.count()
    total_appointments = Appointment.query.count()
    
    return jsonify({
        'totalUsers': total_users,
        'totalAssessments': total_assessments,
        'totalAppointments': total_appointments
    })

# ==================== INIT DATABASE ====================

def init_db():
    with app.app_context():
        db.create_all()
        print("✅ Database tables created!")

# ==================== RUN SERVER ====================

if __name__ == '__main__':
    init_db()
    print("\n" + "="*50)
    print("🚀 MENTAL WELLNESS PORTAL BACKEND")
    print("="*50)
    print("📍 Server running at: http://127.0.0.1:5000")
    print("📍 Test routes:")
    print("   • http://127.0.0.1:5000/")
    print("   • http://127.0.0.1:5000/test")
    print("   • http://127.0.0.1:5000/api/counsellors")
    print("="*50 + "\n")
    app.run(debug=True, port=5000)