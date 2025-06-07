from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt
from src.models import Topic, Lesson, Exercise, db, UserRole

curriculum_bp = Blueprint('curriculum', __name__)

# Topic routes
@curriculum_bp.route('/topics', methods=['GET'])
def get_topics():
    """Get all topics, optionally filtered by year group."""
    year_group = request.args.get('year_group', type=int)
    
    query = Topic.query
    if year_group:
        query = query.filter_by(year_group=year_group)
    
    topics = query.order_by(Topic.year_group, Topic.order).all()
    return jsonify([topic.to_dict() for topic in topics])

@curriculum_bp.route('/topics/<int:topic_id>', methods=['GET'])
def get_topic(topic_id):
    """Get a specific topic by ID."""
    topic = Topic.query.get_or_404(topic_id)
    return jsonify(topic.to_dict())

@curriculum_bp.route('/topics', methods=['POST'])
@jwt_required()
def create_topic():
    """Create a new topic (admin only)."""
    # Check if user is admin
    jwt_data = get_jwt()
    if jwt_data.get('role') != UserRole.ADMIN.value:
        return jsonify({"error": "Admin access required"}), 403
    
    data = request.json
    
    # Check required fields
    required_fields = ['name', 'year_group']
    for field in required_fields:
        if field not in data:
            return jsonify({"error": f"Missing required field: {field}"}), 400
    
    # Create topic
    topic = Topic(
        name=data['name'],
        description=data.get('description', ''),
        icon=data.get('icon', ''),
        year_group=data['year_group'],
        order=data.get('order', 0)
    )
    
    db.session.add(topic)
    db.session.commit()
    
    return jsonify(topic.to_dict()), 201

@curriculum_bp.route('/topics/<int:topic_id>', methods=['PUT'])
@jwt_required()
def update_topic(topic_id):
    """Update a topic (admin only)."""
    # Check if user is admin
    jwt_data = get_jwt()
    if jwt_data.get('role') != UserRole.ADMIN.value:
        return jsonify({"error": "Admin access required"}), 403
    
    topic = Topic.query.get_or_404(topic_id)
    data = request.json
    
    # Update fields
    if 'name' in data:
        topic.name = data['name']
    if 'description' in data:
        topic.description = data['description']
    if 'icon' in data:
        topic.icon = data['icon']
    if 'year_group' in data:
        topic.year_group = data['year_group']
    if 'order' in data:
        topic.order = data['order']
    
    db.session.commit()
    
    return jsonify(topic.to_dict())

@curriculum_bp.route('/topics/<int:topic_id>', methods=['DELETE'])
@jwt_required()
def delete_topic(topic_id):
    """Delete a topic (admin only)."""
    # Check if user is admin
    jwt_data = get_jwt()
    if jwt_data.get('role') != UserRole.ADMIN.value:
        return jsonify({"error": "Admin access required"}), 403
    
    topic = Topic.query.get_or_404(topic_id)
    db.session.delete(topic)
    db.session.commit()
    
    return '', 204

# Lesson routes
@curriculum_bp.route('/topics/<int:topic_id>/lessons', methods=['GET'])
def get_lessons(topic_id):
    """Get all lessons for a topic."""
    Topic.query.get_or_404(topic_id)  # Check if topic exists
    lessons = Lesson.query.filter_by(topic_id=topic_id).order_by(Lesson.order).all()
    return jsonify([lesson.to_dict() for lesson in lessons])

@curriculum_bp.route('/lessons/<int:lesson_id>', methods=['GET'])
def get_lesson(lesson_id):
    """Get a specific lesson by ID."""
    lesson = Lesson.query.get_or_404(lesson_id)
    return jsonify(lesson.to_dict())

@curriculum_bp.route('/topics/<int:topic_id>/lessons', methods=['POST'])
@jwt_required()
def create_lesson(topic_id):
    """Create a new lesson for a topic (admin only)."""
    # Check if user is admin
    jwt_data = get_jwt()
    if jwt_data.get('role') != UserRole.ADMIN.value:
        return jsonify({"error": "Admin access required"}), 403
    
    Topic.query.get_or_404(topic_id)  # Check if topic exists
    data = request.json
    
    # Check required fields
    required_fields = ['title', 'content']
    for field in required_fields:
        if field not in data:
            return jsonify({"error": f"Missing required field: {field}"}), 400
    
    # Create lesson
    lesson = Lesson(
        topic_id=topic_id,
        title=data['title'],
        description=data.get('description', ''),
        content=data['content'],
        order=data.get('order', 0),
        difficulty=data.get('difficulty', 1),
        estimated_time=data.get('estimated_time')
    )
    
    db.session.add(lesson)
    db.session.commit()
    
    return jsonify(lesson.to_dict()), 201

@curriculum_bp.route('/lessons/<int:lesson_id>', methods=['PUT'])
@jwt_required()
def update_lesson(lesson_id):
    """Update a lesson (admin only)."""
    # Check if user is admin
    jwt_data = get_jwt()
    if jwt_data.get('role') != UserRole.ADMIN.value:
        return jsonify({"error": "Admin access required"}), 403
    
    lesson = Lesson.query.get_or_404(lesson_id)
    data = request.json
    
    # Update fields
    if 'title' in data:
        lesson.title = data['title']
    if 'description' in data:
        lesson.description = data['description']
    if 'content' in data:
        lesson.content = data['content']
    if 'order' in data:
        lesson.order = data['order']
    if 'difficulty' in data:
        lesson.difficulty = data['difficulty']
    if 'estimated_time' in data:
        lesson.estimated_time = data['estimated_time']
    
    db.session.commit()
    
    return jsonify(lesson.to_dict())

@curriculum_bp.route('/lessons/<int:lesson_id>', methods=['DELETE'])
@jwt_required()
def delete_lesson(lesson_id):
    """Delete a lesson (admin only)."""
    # Check if user is admin
    jwt_data = get_jwt()
    if jwt_data.get('role') != UserRole.ADMIN.value:
        return jsonify({"error": "Admin access required"}), 403
    
    lesson = Lesson.query.get_or_404(lesson_id)
    db.session.delete(lesson)
    db.session.commit()
    
    return '', 204

# Exercise routes
@curriculum_bp.route('/lessons/<int:lesson_id>/exercises', methods=['GET'])
def get_exercises(lesson_id):
    """Get all exercises for a lesson."""
    Lesson.query.get_or_404(lesson_id)  # Check if lesson exists
    exercises = Exercise.query.filter_by(lesson_id=lesson_id).order_by(Exercise.order).all()
    return jsonify([exercise.to_dict() for exercise in exercises])

@curriculum_bp.route('/exercises/<int:exercise_id>', methods=['GET'])
def get_exercise(exercise_id):
    """Get a specific exercise by ID."""
    exercise = Exercise.query.get_or_404(exercise_id)
    return jsonify(exercise.to_dict())

@curriculum_bp.route('/lessons/<int:lesson_id>/exercises', methods=['POST'])
@jwt_required()
def create_exercise(lesson_id):
    """Create a new exercise for a lesson (admin only)."""
    # Check if user is admin
    jwt_data = get_jwt()
    if jwt_data.get('role') != UserRole.ADMIN.value:
        return jsonify({"error": "Admin access required"}), 403
    
    Lesson.query.get_or_404(lesson_id)  # Check if lesson exists
    data = request.json
    
    # Check required fields
    required_fields = ['title', 'question_type', 'question_data', 'answer_data']
    for field in required_fields:
        if field not in data:
            return jsonify({"error": f"Missing required field: {field}"}), 400
    
    # Create exercise
    exercise = Exercise(
        lesson_id=lesson_id,
        title=data['title'],
        description=data.get('description', ''),
        question_type=data['question_type'],
        question_data=data['question_data'],
        answer_data=data['answer_data'],
        difficulty=data.get('difficulty', 1),
        order=data.get('order', 0)
    )
    
    db.session.add(exercise)
    db.session.commit()
    
    return jsonify(exercise.to_dict()), 201

@curriculum_bp.route('/exercises/<int:exercise_id>', methods=['PUT'])
@jwt_required()
def update_exercise(exercise_id):
    """Update an exercise (admin only)."""
    # Check if user is admin
    jwt_data = get_jwt()
    if jwt_data.get('role') != UserRole.ADMIN.value:
        return jsonify({"error": "Admin access required"}), 403
    
    exercise = Exercise.query.get_or_404(exercise_id)
    data = request.json
    
    # Update fields
    if 'title' in data:
        exercise.title = data['title']
    if 'description' in data:
        exercise.description = data['description']
    if 'question_type' in data:
        exercise.question_type = data['question_type']
    if 'question_data' in data:
        exercise.question_data = data['question_data']
    if 'answer_data' in data:
        exercise.answer_data = data['answer_data']
    if 'difficulty' in data:
        exercise.difficulty = data['difficulty']
    if 'order' in data:
        exercise.order = data['order']
    
    db.session.commit()
    
    return jsonify(exercise.to_dict())

@curriculum_bp.route('/exercises/<int:exercise_id>', methods=['DELETE'])
@jwt_required()
def delete_exercise(exercise_id):
    """Delete an exercise (admin only)."""
    # Check if user is admin
    jwt_data = get_jwt()
    if jwt_data.get('role') != UserRole.ADMIN.value:
        return jsonify({"error": "Admin access required"}), 403
    
    exercise = Exercise.query.get_or_404(exercise_id)
    db.session.delete(exercise)
    db.session.commit()
    
    return '', 204

