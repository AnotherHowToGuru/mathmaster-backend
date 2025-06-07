from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from datetime import datetime, date
from src.models import (
    ProgressRecord, LessonProgress, TopicProgress, DailyActivity,
    ChildProfile, Exercise, Lesson, Topic, User, UserRole, db
)

progress_bp = Blueprint('progress', __name__)

# Helper function to check if user has access to child data
def check_child_access(child_id, user_id, user_role):
    """Check if the user has access to the child's data."""
    if user_role == UserRole.ADMIN.value:
        return True
    
    if user_role == UserRole.CHILD.value:
        # Child can only access their own data
        child = ChildProfile.query.filter_by(user_id=user_id).first()
        return child and child.id == child_id
    
    if user_role == UserRole.PARENT.value:
        # Parent can access their children's data
        child = ChildProfile.query.get(child_id)
        return child and child.parent and child.parent.user_id == user_id
    
    return False

# Progress record routes
@progress_bp.route('/children/<int:child_id>/progress/exercises/<int:exercise_id>', methods=['POST'])
@jwt_required()
def record_exercise_progress(child_id, exercise_id):
    """Record progress for an exercise."""
    # Check access
    user_id = get_jwt_identity()
    user_role = get_jwt().get('role')
    
    if not check_child_access(child_id, user_id, user_role):
        return jsonify({"error": "Access denied"}), 403
    
    # Check if exercise exists
    exercise = Exercise.query.get_or_404(exercise_id)
    
    data = request.json
    
    # Check required fields
    if 'score' not in data:
        return jsonify({"error": "Missing required field: score"}), 400
    
    # Create or update progress record
    progress = ProgressRecord.query.filter_by(
        child_id=child_id,
        exercise_id=exercise_id
    ).first()
    
    if progress:
        # Update existing record
        progress.score = data['score']
        progress.time_spent = data.get('time_spent', progress.time_spent)
        progress.attempts += 1
        progress.completed = data.get('completed', progress.completed)
    else:
        # Create new record
        progress = ProgressRecord(
            child_id=child_id,
            exercise_id=exercise_id,
            score=data['score'],
            time_spent=data.get('time_spent'),
            attempts=1,
            completed=data.get('completed', False)
        )
        db.session.add(progress)
    
    # Update lesson progress
    lesson_progress = LessonProgress.query.filter_by(
        child_id=child_id,
        lesson_id=exercise.lesson_id
    ).first()
    
    if not lesson_progress:
        lesson_progress = LessonProgress(
            child_id=child_id,
            lesson_id=exercise.lesson_id,
            status='in_progress'
        )
        db.session.add(lesson_progress)
    
    # Calculate lesson progress percentage
    total_exercises = Exercise.query.filter_by(lesson_id=exercise.lesson_id).count()
    completed_exercises = ProgressRecord.query.filter_by(
        child_id=child_id,
        completed=True
    ).join(Exercise).filter(Exercise.lesson_id == exercise.lesson_id).count()
    
    if data.get('completed', False):
        completed_exercises += 1
    
    if total_exercises > 0:
        lesson_progress.progress_percentage = (completed_exercises / total_exercises) * 100
        
        # Update lesson status if all exercises are completed
        if completed_exercises == total_exercises:
            lesson_progress.status = 'completed'
    
    # Update topic progress
    lesson = Lesson.query.get(exercise.lesson_id)
    topic_progress = TopicProgress.query.filter_by(
        child_id=child_id,
        topic_id=lesson.topic_id
    ).first()
    
    if not topic_progress:
        topic_progress = TopicProgress(
            child_id=child_id,
            topic_id=lesson.topic_id
        )
        db.session.add(topic_progress)
    
    # Calculate topic progress percentage
    total_lessons = Lesson.query.filter_by(topic_id=lesson.topic_id).count()
    completed_lessons = LessonProgress.query.filter_by(
        child_id=child_id,
        status='completed'
    ).join(Lesson).filter(Lesson.topic_id == lesson.topic_id).count()
    
    if total_lessons > 0:
        topic_progress.progress_percentage = (completed_lessons / total_lessons) * 100
        topic_progress.lessons_completed = completed_lessons
    
    # Update exercises completed count
    topic_progress.exercises_completed = ProgressRecord.query.filter_by(
        child_id=child_id,
        completed=True
    ).join(Exercise).join(Lesson).filter(Lesson.topic_id == lesson.topic_id).count()
    
    # Update daily activity
    today = date.today()
    daily_activity = DailyActivity.query.filter_by(
        child_id=child_id,
        date=today
    ).first()
    
    if not daily_activity:
        daily_activity = DailyActivity(
            child_id=child_id,
            date=today
        )
        db.session.add(daily_activity)
    
    daily_activity.exercises_completed += 1
    if data.get('time_spent'):
        daily_activity.time_spent += data['time_spent']
    
    # Calculate average score for the day
    daily_scores = ProgressRecord.query.filter_by(
        child_id=child_id
    ).filter(
        db.func.date(ProgressRecord.created_at) == today
    ).with_entities(ProgressRecord.score).all()
    
    if daily_scores:
        daily_activity.average_score = sum(score[0] for score in daily_scores) / len(daily_scores)
    
    db.session.commit()
    
    return jsonify(progress.to_dict()), 201

@progress_bp.route('/children/<int:child_id>/progress/lessons/<int:lesson_id>', methods=['POST'])
@jwt_required()
def update_lesson_progress(child_id, lesson_id):
    """Update progress for a lesson."""
    # Check access
    user_id = get_jwt_identity()
    user_role = get_jwt().get('role')
    
    if not check_child_access(child_id, user_id, user_role):
        return jsonify({"error": "Access denied"}), 403
    
    # Check if lesson exists
    lesson = Lesson.query.get_or_404(lesson_id)
    
    data = request.json
    
    # Create or update lesson progress
    lesson_progress = LessonProgress.query.filter_by(
        child_id=child_id,
        lesson_id=lesson_id
    ).first()
    
    if not lesson_progress:
        lesson_progress = LessonProgress(
            child_id=child_id,
            lesson_id=lesson_id,
            status=data.get('status', 'in_progress'),
            progress_percentage=data.get('progress_percentage', 0.0),
            last_position=data.get('last_position'),
            time_spent=data.get('time_spent', 0)
        )
        db.session.add(lesson_progress)
    else:
        if 'status' in data:
            lesson_progress.status = data['status']
        if 'progress_percentage' in data:
            lesson_progress.progress_percentage = data['progress_percentage']
        if 'last_position' in data:
            lesson_progress.last_position = data['last_position']
        if 'time_spent' in data:
            lesson_progress.time_spent += data['time_spent']
    
    # Update topic progress if lesson is completed
    if data.get('status') == 'completed':
        topic_progress = TopicProgress.query.filter_by(
            child_id=child_id,
            topic_id=lesson.topic_id
        ).first()
        
        if not topic_progress:
            topic_progress = TopicProgress(
                child_id=child_id,
                topic_id=lesson.topic_id
            )
            db.session.add(topic_progress)
        
        # Calculate topic progress percentage
        total_lessons = Lesson.query.filter_by(topic_id=lesson.topic_id).count()
        completed_lessons = LessonProgress.query.filter_by(
            child_id=child_id,
            status='completed'
        ).join(Lesson).filter(Lesson.topic_id == lesson.topic_id).count() + 1  # +1 for current lesson
        
        if total_lessons > 0:
            topic_progress.progress_percentage = (completed_lessons / total_lessons) * 100
            topic_progress.lessons_completed = completed_lessons
    
    # Update daily activity
    today = date.today()
    daily_activity = DailyActivity.query.filter_by(
        child_id=child_id,
        date=today
    ).first()
    
    if not daily_activity:
        daily_activity = DailyActivity(
            child_id=child_id,
            date=today
        )
        db.session.add(daily_activity)
    
    daily_activity.lessons_viewed += 1
    if data.get('time_spent'):
        daily_activity.time_spent += data['time_spent']
    
    db.session.commit()
    
    return jsonify(lesson_progress.to_dict()), 200

# Progress retrieval routes
@progress_bp.route('/children/<int:child_id>/progress/exercises', methods=['GET'])
@jwt_required()
def get_exercise_progress(child_id):
    """Get progress for all exercises for a child."""
    # Check access
    user_id = get_jwt_identity()
    user_role = get_jwt().get('role')
    
    if not check_child_access(child_id, user_id, user_role):
        return jsonify({"error": "Access denied"}), 403
    
    # Filter by lesson if provided
    lesson_id = request.args.get('lesson_id', type=int)
    
    query = ProgressRecord.query.filter_by(child_id=child_id)
    if lesson_id:
        query = query.join(Exercise).filter(Exercise.lesson_id == lesson_id)
    
    progress_records = query.all()
    return jsonify([record.to_dict() for record in progress_records])

@progress_bp.route('/children/<int:child_id>/progress/lessons', methods=['GET'])
@jwt_required()
def get_lesson_progress(child_id):
    """Get progress for all lessons for a child."""
    # Check access
    user_id = get_jwt_identity()
    user_role = get_jwt().get('role')
    
    if not check_child_access(child_id, user_id, user_role):
        return jsonify({"error": "Access denied"}), 403
    
    # Filter by topic if provided
    topic_id = request.args.get('topic_id', type=int)
    
    query = LessonProgress.query.filter_by(child_id=child_id)
    if topic_id:
        query = query.join(Lesson).filter(Lesson.topic_id == topic_id)
    
    lesson_progress = query.all()
    return jsonify([progress.to_dict() for progress in lesson_progress])

@progress_bp.route('/children/<int:child_id>/progress/topics', methods=['GET'])
@jwt_required()
def get_topic_progress(child_id):
    """Get progress for all topics for a child."""
    # Check access
    user_id = get_jwt_identity()
    user_role = get_jwt().get('role')
    
    if not check_child_access(child_id, user_id, user_role):
        return jsonify({"error": "Access denied"}), 403
    
    # Filter by year group if provided
    year_group = request.args.get('year_group', type=int)
    
    query = TopicProgress.query.filter_by(child_id=child_id)
    if year_group:
        query = query.join(Topic).filter(Topic.year_group == year_group)
    
    topic_progress = query.all()
    return jsonify([progress.to_dict() for progress in topic_progress])

@progress_bp.route('/children/<int:child_id>/activity', methods=['GET'])
@jwt_required()
def get_daily_activity(child_id):
    """Get daily activity for a child."""
    # Check access
    user_id = get_jwt_identity()
    user_role = get_jwt().get('role')
    
    if not check_child_access(child_id, user_id, user_role):
        return jsonify({"error": "Access denied"}), 403
    
    # Filter by date range if provided
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    
    query = DailyActivity.query.filter_by(child_id=child_id)
    
    if start_date:
        query = query.filter(DailyActivity.date >= start_date)
    if end_date:
        query = query.filter(DailyActivity.date <= end_date)
    
    activities = query.order_by(DailyActivity.date.desc()).all()
    return jsonify([activity.to_dict() for activity in activities])

@progress_bp.route('/children/<int:child_id>/summary', methods=['GET'])
@jwt_required()
def get_progress_summary(child_id):
    """Get a summary of progress for a child."""
    # Check access
    user_id = get_jwt_identity()
    user_role = get_jwt().get('role')
    
    if not check_child_access(child_id, user_id, user_role):
        return jsonify({"error": "Access denied"}), 403
    
    # Get child profile
    child = ChildProfile.query.get_or_404(child_id)
    
    # Get overall progress statistics
    total_topics = Topic.query.filter_by(year_group=child.year_group).count()
    completed_topics = TopicProgress.query.filter_by(
        child_id=child_id,
        progress_percentage=100
    ).count()
    
    total_lessons = Lesson.query.join(Topic).filter(Topic.year_group == child.year_group).count()
    completed_lessons = LessonProgress.query.filter_by(
        child_id=child_id,
        status='completed'
    ).count()
    
    total_exercises = Exercise.query.join(Lesson).join(Topic).filter(Topic.year_group == child.year_group).count()
    completed_exercises = ProgressRecord.query.filter_by(
        child_id=child_id,
        completed=True
    ).count()
    
    # Calculate average scores
    average_score = db.session.query(db.func.avg(ProgressRecord.score)).filter_by(child_id=child_id).scalar() or 0
    
    # Get recent activity
    recent_activity = DailyActivity.query.filter_by(child_id=child_id).order_by(DailyActivity.date.desc()).limit(7).all()
    
    # Calculate total time spent
    total_time_spent = db.session.query(db.func.sum(DailyActivity.time_spent)).filter_by(child_id=child_id).scalar() or 0
    
    return jsonify({
        "child_id": child_id,
        "year_group": child.year_group,
        "topics": {
            "total": total_topics,
            "completed": completed_topics,
            "percentage": (completed_topics / total_topics * 100) if total_topics > 0 else 0
        },
        "lessons": {
            "total": total_lessons,
            "completed": completed_lessons,
            "percentage": (completed_lessons / total_lessons * 100) if total_lessons > 0 else 0
        },
        "exercises": {
            "total": total_exercises,
            "completed": completed_exercises,
            "percentage": (completed_exercises / total_exercises * 100) if total_exercises > 0 else 0
        },
        "average_score": average_score,
        "total_time_spent": total_time_spent,
        "recent_activity": [activity.to_dict() for activity in recent_activity]
    })

