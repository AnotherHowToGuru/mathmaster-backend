from datetime import datetime
from src.models.user import db

class AchievementType(db.Model):
    __tablename__ = 'achievement_types'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    icon = db.Column(db.String(100))
    badge_image = db.Column(db.String(100))
    points = db.Column(db.Integer, default=10)
    criteria = db.Column(db.Text)  # JSON data for achievement criteria
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    achievements = db.relationship('Achievement', backref='achievement_type', lazy=True)
    
    def __repr__(self):
        return f'<AchievementType {self.name}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'icon': self.icon,
            'badge_image': self.badge_image,
            'points': self.points,
            'criteria': self.criteria,
            'created_at': self.created_at.isoformat()
        }

class Achievement(db.Model):
    __tablename__ = 'achievements'
    
    id = db.Column(db.Integer, primary_key=True)
    child_id = db.Column(db.Integer, db.ForeignKey('child_profiles.id'), nullable=False)
    achievement_type_id = db.Column(db.Integer, db.ForeignKey('achievement_types.id'), nullable=False)
    earned_at = db.Column(db.DateTime, default=datetime.utcnow)
    viewed = db.Column(db.Boolean, default=False)
    
    def __repr__(self):
        return f'<Achievement Child:{self.child_id} Type:{self.achievement_type_id}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'child_id': self.child_id,
            'achievement_type_id': self.achievement_type_id,
            'earned_at': self.earned_at.isoformat(),
            'viewed': self.viewed,
            'achievement_type': self.achievement_type.to_dict() if self.achievement_type else None
        }

class Reward(db.Model):
    __tablename__ = 'rewards'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    image = db.Column(db.String(100))
    points_required = db.Column(db.Integer, nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    child_rewards = db.relationship('ChildReward', backref='reward', lazy=True)
    
    def __repr__(self):
        return f'<Reward {self.name}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'image': self.image,
            'points_required': self.points_required,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat()
        }

class ChildReward(db.Model):
    __tablename__ = 'child_rewards'
    
    id = db.Column(db.Integer, primary_key=True)
    child_id = db.Column(db.Integer, db.ForeignKey('child_profiles.id'), nullable=False)
    reward_id = db.Column(db.Integer, db.ForeignKey('rewards.id'), nullable=False)
    earned_at = db.Column(db.DateTime, default=datetime.utcnow)
    redeemed = db.Column(db.Boolean, default=False)
    redeemed_at = db.Column(db.DateTime)
    
    def __repr__(self):
        return f'<ChildReward Child:{self.child_id} Reward:{self.reward_id} Redeemed:{self.redeemed}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'child_id': self.child_id,
            'reward_id': self.reward_id,
            'earned_at': self.earned_at.isoformat(),
            'redeemed': self.redeemed,
            'redeemed_at': self.redeemed_at.isoformat() if self.redeemed_at else None,
            'reward': self.reward.to_dict() if self.reward else None
        }

