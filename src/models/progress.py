from datetime import datetime
from src.models.user import db

class ProgressRecord(db.Model):
    __tablename__ = 'progress_records'
    
    id = db.Column(db.Integer, primary_key=True)
    child_id = db.Column(db.Integer, db.ForeignKey('child_profiles.id'), nullable=False)
    exercise_id = db.Column(db.Integer, db.ForeignKey('exercises.id'), nullable=False)
    score = db.Column(db.Float, nullable=False)  # Percentage correct (0-100)
    time_spent = db.Column(db.Integer)  # In seconds
    attempts = db.Column(db.Integer, default=1)
    completed = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<ProgressRecord Child:{self.child_id} Exercise:{self.exercise_id} Score:{self.score}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'child_id': self.child_id,
            'exercise_id': self.exercise_id,
            'score': self.score,
            'time_spent': self.time_spent,
            'attempts': self.attempts,
            'completed': self.completed,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }

class LessonProgress(db.Model):
    __tablename__ = 'lesson_progress'
    
    id = db.Column(db.Integer, primary_key=True)
    child_id = db.Column(db.Integer, db.ForeignKey('child_profiles.id'), nullable=False)
    lesson_id = db.Column(db.Integer, db.ForeignKey('lessons.id'), nullable=False)
    status = db.Column(db.String(20), default='not_started')  # not_started, in_progress, completed
    progress_percentage = db.Column(db.Float, default=0.0)  # 0-100
    last_position = db.Column(db.String(50))  # Store position in lesson (e.g., slide number)
    time_spent = db.Column(db.Integer, default=0)  # Total time spent in seconds
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Unique constraint to ensure one progress record per child per lesson
    __table_args__ = (db.UniqueConstraint('child_id', 'lesson_id', name='unique_child_lesson'),)
    
    def __repr__(self):
        return f'<LessonProgress Child:{self.child_id} Lesson:{self.lesson_id} Status:{self.status}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'child_id': self.child_id,
            'lesson_id': self.lesson_id,
            'status': self.status,
            'progress_percentage': self.progress_percentage,
            'last_position': self.last_position,
            'time_spent': self.time_spent,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }

class TopicProgress(db.Model):
    __tablename__ = 'topic_progress'
    
    id = db.Column(db.Integer, primary_key=True)
    child_id = db.Column(db.Integer, db.ForeignKey('child_profiles.id'), nullable=False)
    topic_id = db.Column(db.Integer, db.ForeignKey('topics.id'), nullable=False)
    progress_percentage = db.Column(db.Float, default=0.0)  # 0-100
    lessons_completed = db.Column(db.Integer, default=0)
    exercises_completed = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Unique constraint to ensure one progress record per child per topic
    __table_args__ = (db.UniqueConstraint('child_id', 'topic_id', name='unique_child_topic'),)
    
    def __repr__(self):
        return f'<TopicProgress Child:{self.child_id} Topic:{self.topic_id} Progress:{self.progress_percentage}%>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'child_id': self.child_id,
            'topic_id': self.topic_id,
            'progress_percentage': self.progress_percentage,
            'lessons_completed': self.lessons_completed,
            'exercises_completed': self.exercises_completed,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }

class DailyActivity(db.Model):
    __tablename__ = 'daily_activities'
    
    id = db.Column(db.Integer, primary_key=True)
    child_id = db.Column(db.Integer, db.ForeignKey('child_profiles.id'), nullable=False)
    date = db.Column(db.Date, nullable=False)
    time_spent = db.Column(db.Integer, default=0)  # Total time spent in seconds
    lessons_viewed = db.Column(db.Integer, default=0)
    exercises_completed = db.Column(db.Integer, default=0)
    average_score = db.Column(db.Float)  # Average score for exercises completed that day
    
    # Unique constraint to ensure one activity record per child per day
    __table_args__ = (db.UniqueConstraint('child_id', 'date', name='unique_child_date'),)
    
    def __repr__(self):
        return f'<DailyActivity Child:{self.child_id} Date:{self.date} Time:{self.time_spent}s>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'child_id': self.child_id,
            'date': self.date.isoformat(),
            'time_spent': self.time_spent,
            'lessons_viewed': self.lessons_viewed,
            'exercises_completed': self.exercises_completed,
            'average_score': self.average_score
        }

