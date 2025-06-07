from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import enum

db = SQLAlchemy()

class UserRole(enum.Enum):
    PARENT = "parent"
    CHILD = "child"
    ADMIN = "admin"

class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.Enum(UserRole), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationship with ParentProfile
    parent_profile = db.relationship('ParentProfile', backref='user', uselist=False, cascade='all, delete-orphan')
    
    # Relationship with ChildProfile
    child_profile = db.relationship('ChildProfile', backref='user', uselist=False, cascade='all, delete-orphan')

    def __repr__(self):
        return f'<User {self.username}>'

    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'role': self.role.value,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }

class ParentProfile(db.Model):
    __tablename__ = 'parent_profiles'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    first_name = db.Column(db.String(50))
    last_name = db.Column(db.String(50))
    phone_number = db.Column(db.String(20))
    subscription_status = db.Column(db.String(20), default='free')
    subscription_expiry = db.Column(db.DateTime, nullable=True)
    stripe_customer_id = db.Column(db.String(50), nullable=True)
    
    # Relationship with ChildProfile (parent's children)
    children = db.relationship('ChildProfile', backref='parent', lazy=True)
    
    def __repr__(self):
        return f'<ParentProfile {self.first_name} {self.last_name}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'phone_number': self.phone_number,
            'subscription_status': self.subscription_status,
            'subscription_expiry': self.subscription_expiry.isoformat() if self.subscription_expiry else None,
            'children': [child.to_dict() for child in self.children] if self.children else []
        }

class ChildProfile(db.Model):
    __tablename__ = 'child_profiles'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    parent_id = db.Column(db.Integer, db.ForeignKey('parent_profiles.id'), nullable=True)
    first_name = db.Column(db.String(50))
    avatar = db.Column(db.String(100), default='default_avatar.png')
    year_group = db.Column(db.Integer)  # UK school year (1-6)
    date_of_birth = db.Column(db.Date, nullable=True)
    
    # Relationships
    progress_records = db.relationship('ProgressRecord', backref='child', lazy=True)
    achievements = db.relationship('Achievement', backref='child', lazy=True)
    
    def __repr__(self):
        return f'<ChildProfile {self.first_name}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'parent_id': self.parent_id,
            'first_name': self.first_name,
            'avatar': self.avatar,
            'year_group': self.year_group,
            'date_of_birth': self.date_of_birth.isoformat() if self.date_of_birth else None
        }

