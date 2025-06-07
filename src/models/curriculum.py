from datetime import datetime
from src.models.user import db

class Topic(db.Model):
    __tablename__ = 'topics'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    icon = db.Column(db.String(100))
    year_group = db.Column(db.Integer)  # UK school year (1-6)
    order = db.Column(db.Integer, default=0)  # For ordering topics within a year group
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    lessons = db.relationship('Lesson', backref='topic', lazy=True, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Topic {self.name} (Year {self.year_group})>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'icon': self.icon,
            'year_group': self.year_group,
            'order': self.order,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'lesson_count': len(self.lessons)
        }

class Lesson(db.Model):
    __tablename__ = 'lessons'
    
    id = db.Column(db.Integer, primary_key=True)
    topic_id = db.Column(db.Integer, db.ForeignKey('topics.id'), nullable=False)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    content = db.Column(db.Text, nullable=False)  # JSON content for the lesson
    order = db.Column(db.Integer, default=0)  # For ordering lessons within a topic
    difficulty = db.Column(db.Integer, default=1)  # 1-5 scale
    estimated_time = db.Column(db.Integer)  # In minutes
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    exercises = db.relationship('Exercise', backref='lesson', lazy=True, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Lesson {self.title}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'topic_id': self.topic_id,
            'title': self.title,
            'description': self.description,
            'content': self.content,
            'order': self.order,
            'difficulty': self.difficulty,
            'estimated_time': self.estimated_time,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'exercise_count': len(self.exercises)
        }

class Exercise(db.Model):
    __tablename__ = 'exercises'
    
    id = db.Column(db.Integer, primary_key=True)
    lesson_id = db.Column(db.Integer, db.ForeignKey('lessons.id'), nullable=False)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    question_type = db.Column(db.String(50), nullable=False)  # multiple_choice, fill_in_blank, etc.
    question_data = db.Column(db.Text, nullable=False)  # JSON data for the question
    answer_data = db.Column(db.Text, nullable=False)  # JSON data for the answer
    difficulty = db.Column(db.Integer, default=1)  # 1-5 scale
    order = db.Column(db.Integer, default=0)  # For ordering exercises within a lesson
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    progress_records = db.relationship('ProgressRecord', backref='exercise', lazy=True)
    
    def __repr__(self):
        return f'<Exercise {self.title}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'lesson_id': self.lesson_id,
            'title': self.title,
            'description': self.description,
            'question_type': self.question_type,
            'question_data': self.question_data,
            'difficulty': self.difficulty,
            'order': self.order,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }

