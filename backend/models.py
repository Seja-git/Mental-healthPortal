from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    anonymous_id = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(200))
    role = db.Column(db.String(50))  # student, counsellor, volunteer, organization
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    assessments = db.relationship('Assessment', backref='user', lazy=True)
    appointments = db.relationship('Appointment', backref='user', lazy=True)
    forum_posts = db.relationship('ForumPost', backref='user', lazy=True)
    complaints = db.relationship('Complaint', backref='user', lazy=True)
    feedbacks = db.relationship('Feedback', backref='user', lazy=True)
    
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
    user_id = db.Column(db.String(50), db.ForeignKey('users.anonymous_id'), nullable=False)
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
    user_id = db.Column(db.String(50), db.ForeignKey('users.anonymous_id'), nullable=False)
    counsellor_id = db.Column(db.String(50), db.ForeignKey('users.anonymous_id'))
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
    user_id = db.Column(db.String(50), db.ForeignKey('users.anonymous_id'))
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
            'anonymous': self.anonymous,
            'moderated': self.is_moderated
        }

class Complaint(db.Model):
    __tablename__ = 'complaints'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(50), db.ForeignKey('users.anonymous_id'))
    category = db.Column(db.String(50))
    complaint = db.Column(db.Text)
    anonymous = db.Column(db.Boolean, default=True)
    tracking_number = db.Column(db.String(50), unique=True)
    status = db.Column(db.String(20), default='pending')  # pending, reviewing, resolved, closed
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
            'created_at': self.created_at.isoformat(),
            'anonymous': self.anonymous
        }

class Feedback(db.Model):
    __tablename__ = 'feedbacks'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(50), db.ForeignKey('users.anonymous_id'))
    rating = db.Column(db.Integer)  # 1-5
    feedback = db.Column(db.Text)
    suggestion = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'rating': self.rating,
            'feedback': self.feedback,
            'suggestion': self.suggestion,
            'created_at': self.created_at.isoformat()
        }

class CrisisAlert(db.Model):
    __tablename__ = 'crisis_alerts'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(50), db.ForeignKey('users.anonymous_id'))
    assessment_id = db.Column(db.Integer, db.ForeignKey('assessments.id'))
    severity = db.Column(db.String(20))  # high, critical
    message = db.Column(db.Text)
    resolved = db.Column(db.Boolean, default=False)
    resolved_by = db.Column(db.String(50))
    resolved_at = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Resource(db.Model):
    __tablename__ = 'resources'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200))
    type = db.Column(db.String(50))  # video, audio, guide, article
    category = db.Column(db.String(50))  # stress, anxiety, depression, sleep
    language = db.Column(db.String(10))  # en, hi, mr
    url = db.Column(db.String(500))
    thumbnail = db.Column(db.String(500))
    views = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'type': self.type,
            'category': self.category,
            'language': self.language,
            'url': self.url,
            'thumbnail': self.thumbnail,
            'views': self.views
        }

class Notification(db.Model):
    __tablename__ = 'notifications'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(50), db.ForeignKey('users.anonymous_id'))
    type = db.Column(db.String(50))  # appointment, assessment, crisis, forum
    title = db.Column(db.String(200))
    message = db.Column(db.Text)
    read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'type': self.type,
            'title': self.title,
            'message': self.message,
            'read': self.read,
            'created_at': self.created_at.isoformat()
        }