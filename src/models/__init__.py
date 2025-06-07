# Import all models to make them available when importing from models
from src.models.user import db, User, UserRole, ParentProfile, ChildProfile
from src.models.curriculum import Topic, Lesson, Exercise
from src.models.progress import ProgressRecord, LessonProgress, TopicProgress, DailyActivity
from src.models.achievement import AchievementType, Achievement, Reward, ChildReward

# This allows importing all models from src.models
__all__ = [
    'db',
    'User',
    'UserRole',
    'ParentProfile',
    'ChildProfile',
    'Topic',
    'Lesson',
    'Exercise',
    'ProgressRecord',
    'LessonProgress',
    'TopicProgress',
    'DailyActivity',
    'AchievementType',
    'Achievement',
    'Reward',
    'ChildReward'
]

