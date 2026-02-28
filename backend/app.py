from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from datetime import datetime, timedelta
import bcrypt
import os
import json
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
CORS(app)

# Configuration
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'your-secret-key-change-this')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///mental_health.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'jwt-secret-key-change-this')
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(days=1)

db = SQLAlchemy(app)
jwt = JWTManager(app)

# ==================== DATABASE MODELS ====================

class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    anonymous_id = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(200))
    role = db.Column(db.String(50))  # student, counsellor, volunteer, organization
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.anonymous_id,
            'email': self.email,
            'role': self.role,
            'created_at': self.created_at.isoformat()
        }

class Assessment(db.Model):
    __tablename__ = 'assessments'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(50), nullable=False)
    category = db.Column(db.String(50))  # phq9, gad7, stress, sleep
    score = db.Column(db.Integer)
    severity = db.Column(db.String(50))
    responses = db.Column(db.Text)  # JSON string of answers
    date = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'category': self.category,
            'score': self.score,
            'severity': self.severity,
            'date': self.date.isoformat()
        }

class Appointment(db.Model):
    __tablename__ = 'appointments'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(50), nullable=False)
    counsellor_id = db.Column(db.String(50))
    student_name = db.Column(db.String(100))
    email = db.Column(db.String(100))
    phone = db.Column(db.String(20))
    mode = db.Column(db.String(20))  # online, in-person
    counsellor = db.Column(db.String(100))
    date = db.Column(db.String(20))
    time = db.Column(db.String(20))
    duration = db.Column(db.String(20))
    notes = db.Column(db.Text)
    status = db.Column(db.String(20), default='pending')  # pending, confirmed, completed, cancelled
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

class ForumPost(db.Model):
    __tablename__ = 'forum_posts'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(50))
    content = db.Column(db.Text)
    anonymous = db.Column(db.Boolean, default=True)
    likes = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_moderated = db.Column(db.Boolean, default=False)
    
    def to_dict(self):
        return {
            'id': self.id,
            'content': self.content,
            'author': 'Anonymous' if self.anonymous else self.user_id,
            'likes': self.likes,
            'date': self.created_at.isoformat(),
            'moderated': self.is_moderated
        }

class Complaint(db.Model):
    __tablename__ = 'complaints'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(50))
    category = db.Column(db.String(50))
    complaint = db.Column(db.Text)
    anonymous = db.Column(db.Boolean, default=True)
    tracking_number = db.Column(db.String(50), unique=True)
    status = db.Column(db.String(20), default='pending')
    attachment = db.Column(db.String(200))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    resolved_at = db.Column(db.DateTime)
    resolved_by = db.Column(db.String(50))
    
    def to_dict(self):
        return {
            'id': self.id,
            'tracking_number': self.tracking_number,
            'category': self.category,
            'status': self.status,
            'created_at': self.created_at.isoformat()
        }

class Feedback(db.Model):
    __tablename__ = 'feedbacks'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(50))
    rating = db.Column(db.Integer)
    feedback = db.Column(db.Text)
    suggestion = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Resource(db.Model):
    __tablename__ = 'resources'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200))
    type = db.Column(db.String(50))  # video, audio, guide, article
    category = db.Column(db.String(50))
    language = db.Column(db.String(10))
    url = db.Column(db.String(500))
    thumbnail = db.Column(db.String(500))
    views = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class CrisisAlert(db.Model):
    __tablename__ = 'crisis_alerts'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(50))
    assessment_id = db.Column(db.Integer)
    severity = db.Column(db.String(20))
    message = db.Column(db.Text)
    resolved = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

# ==================== INIT DATABASE ====================

def init_db():
    with app.app_context():
        db.create_all()
        print("✅ Database tables created!")
        
        # Add sample resources if empty
        if Resource.query.count() == 0:
            samples = [
                Resource(title="Deep Breathing Exercise", type="video", category="stress", language="en",
                        url="https://www.youtube.com/embed/inpok4MKVLM", thumbnail=""),
                Resource(title="5-4-3-2-1 Grounding Technique", type="guide", category="anxiety", language="en",
                        url="/guides/grounding.html", thumbnail=""),
                Resource(title="Sleep Hygiene Tips", type="article", category="sleep", language="en",
                        url="/guides/sleep.html", thumbnail=""),
            ]
            db.session.add_all(samples)
            db.session.commit()
            print("✅ Sample resources added!")

# ==================== AUTHENTICATION ROUTES ====================

@app.route('/api/auth/signup', methods=['POST'])
def signup():
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
    anonymous_id = f"USER_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}_{hash(email)%10000}"
    
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

@app.route('/api/auth/login', methods=['POST'])
def login():
    data = request.json
    email = data.get('email')
    password = data.get('password')
    
    user = User.query.filter_by(email=email).first()
    
    if not user or not bcrypt.checkpw(password.encode('utf-8'), user.password.encode('utf-8')):
        return jsonify({'error': 'Invalid credentials'}), 401
    
    access_token = create_access_token(identity=user.anonymous_id)
    
    return jsonify({
        'token': access_token,
        'user': user.to_dict()
    })

@app.route('/api/auth/me', methods=['GET'])
@jwt_required()
def get_current_user():
    user_id = get_jwt_identity()
    user = User.query.filter_by(anonymous_id=user_id).first()
    
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    return jsonify(user.to_dict())

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
    
    # Check for crisis (PHQ-9 question 9 about self-harm)
    if data['category'] == 'phq9' and data.get('responses') and len(data['responses']) > 8:
        if data['responses'][8] > 0:  # Question about self-harm
            crisis = CrisisAlert(
                user_id=user_id,
                assessment_id=assessment.id,
                severity='HIGH',
                message='User indicated thoughts of self-harm'
            )
            db.session.add(crisis)
            db.session.commit()
            # In production: send email/SMS to counselors
    
    return jsonify(assessment.to_dict()), 201

@app.route('/api/assessments/<user_id>', methods=['GET'])
def get_user_assessments(user_id):
    assessments = Assessment.query.filter_by(user_id=user_id).order_by(Assessment.date.desc()).all()
    return jsonify([a.to_dict() for a in assessments])

@app.route('/api/assessments/latest/<user_id>', methods=['GET'])
def get_latest_assessment(user_id):
    assessment = Assessment.query.filter_by(user_id=user_id).order_by(Assessment.date.desc()).first()
    return jsonify(assessment.to_dict() if assessment else {})

# ==================== APPOINTMENT ROUTES ====================

@app.route('/api/appointments', methods=['POST'])
@jwt_required()
def create_appointment():
    user_id = get_jwt_identity()
    data = request.json
    
    # Generate meet link for online appointments
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

@app.route('/api/appointments/counsellor', methods=['GET'])
@jwt_required()
def get_counsellor_appointments():
    user_id = get_jwt_identity()
    user = User.query.filter_by(anonymous_id=user_id).first()
    
    if user.role != 'counsellor':
        return jsonify({'error': 'Unauthorized'}), 403
    
    appointments = Appointment.query.filter_by(counsellor_id=user_id).order_by(Appointment.date).all()
    return jsonify([a.to_dict() for a in appointments])

@app.route('/api/appointments/<int:id>/status', methods=['PUT'])
@jwt_required()
def update_appointment_status(id):
    user_id = get_jwt_identity()
    data = request.json
    status = data.get('status')
    
    appointment = Appointment.query.get_or_404(id)
    
    # If confirming, assign this counsellor
    if status == 'confirmed' and not appointment.counsellor_id:
        appointment.counsellor_id = user_id
    
    appointment.status = status
    db.session.commit()
    
    return jsonify({'status': 'updated'})

# ==================== FORUM ROUTES ====================

@app.route('/api/posts', methods=['GET'])
def get_posts():
    posts = ForumPost.query.filter_by(is_moderated=True).order_by(ForumPost.created_at.desc()).limit(50).all()
    return jsonify([p.to_dict() for p in posts])

@app.route('/api/posts', methods=['POST'])
@jwt_required()
def create_post():
    user_id = get_jwt_identity()
    data = request.json
    
    post = ForumPost(
        user_id=user_id,
        content=data['content'],
        anonymous=data.get('anonymous', True)
    )
    
    db.session.add(post)
    db.session.commit()
    
    return jsonify({'id': post.id, 'status': 'pending_moderation'}), 201

@app.route('/api/posts/<int:id>/like', methods=['POST'])
def like_post(id):
    post = ForumPost.query.get_or_404(id)
    post.likes += 1
    db.session.commit()
    return jsonify({'likes': post.likes})

# ==================== COMPLAINT ROUTES ====================

@app.route('/api/complaints', methods=['POST'])
@jwt_required()
def submit_complaint():
    user_id = get_jwt_identity()
    data = request.json
    
    tracking_number = f"CMP{datetime.utcnow().strftime('%Y%m%d%H%M%S')}{hash(user_id)%1000}"
    
    complaint = Complaint(
        user_id=user_id,
        category=data['category'],
        complaint=data['complaint'],
        anonymous=data.get('anonymous', True),
        tracking_number=tracking_number,
        attachment=data.get('attachment')
    )
    
    db.session.add(complaint)
    db.session.commit()
    
    return jsonify({
        'tracking_number': tracking_number,
        'status': 'submitted'
    }), 201

@app.route('/api/complaints/<tracking_number>', methods=['GET'])
def get_complaint_status(tracking_number):
    complaint = Complaint.query.filter_by(tracking_number=tracking_number).first()
    if not complaint:
        return jsonify({'error': 'Not found'}), 404
    
    return jsonify({
        'tracking_number': complaint.tracking_number,
        'status': complaint.status,
        'submitted_at': complaint.created_at.isoformat()
    })

# ==================== FEEDBACK ROUTES ====================

@app.route('/api/feedback', methods=['POST'])
@jwt_required()
def submit_feedback():
    user_id = get_jwt_identity()
    data = request.json
    
    feedback = Feedback(
        user_id=user_id,
        rating=data['rating'],
        feedback=data['feedback'],
        suggestion=data.get('suggestion')
    )
    
    db.session.add(feedback)
    db.session.commit()
    
    return jsonify({'status': 'thank you!'}), 201

# ==================== RESOURCE ROUTES ====================

@app.route('/api/resources', methods=['GET'])
def get_resources():
    category = request.args.get('category')
    language = request.args.get('language', 'en')
    
    query = Resource.query
    if category:
        query = query.filter_by(category=category)
    if language:
        query = query.filter_by(language=language)
    
    resources = query.order_by(Resource.views.desc()).all()
    return jsonify([{
        'id': r.id,
        'title': r.title,
        'type': r.type,
        'category': r.category,
        'url': r.url,
        'thumbnail': r.thumbnail
    } for r in resources])

@app.route('/api/resources/<int:id>/view', methods=['POST'])
def track_view(id):
    resource = Resource.query.get_or_404(id)
    resource.views += 1
    db.session.commit()
    return jsonify({'views': resource.views})

# ==================== COUNSELLOR ROUTES ====================

@app.route('/api/counsellors', methods=['GET'])
def get_counsellors():
    counsellors = User.query.filter_by(role='counsellor').all()
    return jsonify([{
        'id': c.anonymous_id,
        'name': f"Dr. {c.email.split('@')[0]}",
        'specialization': 'Mental Health'
    } for c in counsellors])

@app.route('/api/counsellor/stats', methods=['GET'])
@jwt_required()
def get_counsellor_stats():
    user_id = get_jwt_identity()
    user = User.query.filter_by(anonymous_id=user_id).first()
    
    if user.role != 'counsellor':
        return jsonify({'error': 'Unauthorized'}), 403
    
    today = datetime.now().strftime('%Y-%m-%d')
    
    stats = {
        'today_appointments': Appointment.query.filter_by(counsellor_id=user_id, date=today).count(),
        'pending': Appointment.query.filter_by(counsellor_id=user_id, status='pending').count(),
        'total': Appointment.query.filter_by(counsellor_id=user_id).count(),
        'completed': Appointment.query.filter_by(counsellor_id=user_id, status='completed').count()
    }
    
    return jsonify(stats)

# ==================== ADMIN ROUTES ====================

@app.route('/api/admin/stats', methods=['GET'])
@jwt_required()
def get_admin_stats():
    user_id = get_jwt_identity()
    user = User.query.filter_by(anonymous_id=user_id).first()
    
    if user.role != 'organization':
        return jsonify({'error': 'Unauthorized'}), 403
    
    # Get counts
    total_users = User.query.count()
    total_assessments = Assessment.query.count()
    total_appointments = Appointment.query.count()
    pending_complaints = Complaint.query.filter_by(status='pending').count()
    
    # Get crisis alerts
    crisis_count = CrisisAlert.query.filter_by(resolved=False).count()
    
    # Get trends (last 7 days)
    seven_days_ago = datetime.utcnow() - timedelta(days=7)
    
    return jsonify({
        'totalUsers': total_users,
        'totalAssessments': total_assessments,
        'totalAppointments': total_appointments,
        'pendingComplaints': pending_complaints,
        'crisisAlerts': crisis_count,
        'recentActivity': Assessment.query.filter(Assessment.date >= seven_days_ago).count(),
        'severityDistribution': {
            'minimal': Assessment.query.filter_by(severity='Minimal depression').count(),
            'mild': Assessment.query.filter_by(severity='Mild depression').count(),
            'moderate': Assessment.query.filter_by(severity='Moderate depression').count(),
            'severe': Assessment.query.filter_by(severity='Severe depression').count()
        }
    })

# ==================== CHATBOT ROUTE ====================

@app.route('/api/chat', methods=['POST'])
def chat():
    data = request.json
    message = data.get('message', '').lower()
    
    # Crisis keywords
    crisis_keywords = ['suicide', 'kill myself', 'end my life', 'hurt myself', 'die']
    sad_keywords = ['sad', 'depressed', 'hopeless', 'worthless', 'alone']
    anxiety_keywords = ['anxious', 'nervous', 'worry', 'panic', 'scared']
    stress_keywords = ['stress', 'overwhelmed', 'burnout', 'pressure']
    
    if any(keyword in message for keyword in crisis_keywords):
        response = {
            'response': "I'm very concerned. Please reach out immediately:\n\n🇮🇳 NIMHANS Helpline: 080-46110007\n🇮🇳 AIIMS Helpline: 011-26588588\n\nWould you like me to connect you with a counselor?",
            'crisis_detected': True
        }
    elif any(keyword in message for keyword in sad_keywords):
        response = {
            'response': "I hear that you're feeling sad. Would you like to:\n1️⃣ Take a PHQ-9 depression screening\n2️⃣ Talk to a peer volunteer\n3️⃣ Listen to calming music",
            'crisis_detected': False
        }
    elif any(keyword in message for keyword in anxiety_keywords):
        response = {
            'response': "Let's try a quick breathing exercise:\n\n🌬️ Breathe in for 4 seconds\n💨 Hold for 4 seconds\n🌬️ Breathe out for 6 seconds\n\nWant to try more exercises?",
            'crisis_detected': False
        }
    elif any(keyword in message for keyword in stress_keywords):
        response = {
            'response': "Stress is common. Quick tips:\n📝 Break tasks into smaller steps\n🧘 Take short breaks\n🎵 Listen to relaxing music\n\nExplore our stress management resources?",
            'crisis_detected': False
        }
    else:
        response = {
            'response': "I'm here to support you. You can:\n💭 Talk about how you're feeling\n📊 Take a mental health screening\n📅 Book a counselor appointment\n\nWhat would help most?",
            'crisis_detected': False
    }
    
    return jsonify(response)

# ==================== HELPER FUNCTIONS ====================

def generate_meet_code():
    import random
    import string
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=12))

# ==================== START SERVER ====================

if __name__ == '__main__':
    init_db()
    print("\n" + "="*50)
    print("🚀 MENTAL WELLNESS PORTAL BACKEND")
    print("="*50)
    print("✅ All phases implemented:")
    print("   • JWT Authentication")
    print("   • Assessment (PHQ-9/GAD-7)")
    print("   • Appointment Booking")
    print("   • Forum Posts")
    print("   • Complaints & Feedback")
    print("   • Counsellor Dashboard")
    print("   • Admin Analytics")
    print("   • Crisis Detection")
    print("="*50)
    print("📍 Server running at: http://127.0.0.1:5000")
    print("="*50 + "\n")
    app.run(debug=True, port=5000)