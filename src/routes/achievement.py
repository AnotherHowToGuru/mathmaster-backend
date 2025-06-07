from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from src.models import (
    AchievementType, Achievement, Reward, ChildReward,
    ChildProfile, User, UserRole, db
)

achievement_bp = Blueprint('achievement', __name__)

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

# Achievement type routes
@achievement_bp.route('/achievement-types', methods=['GET'])
def get_achievement_types():
    """Get all achievement types."""
    achievement_types = AchievementType.query.all()
    return jsonify([achievement_type.to_dict() for achievement_type in achievement_types])

@achievement_bp.route('/achievement-types/<int:achievement_type_id>', methods=['GET'])
def get_achievement_type(achievement_type_id):
    """Get a specific achievement type."""
    achievement_type = AchievementType.query.get_or_404(achievement_type_id)
    return jsonify(achievement_type.to_dict())

@achievement_bp.route('/achievement-types', methods=['POST'])
@jwt_required()
def create_achievement_type():
    """Create a new achievement type (admin only)."""
    # Check if user is admin
    jwt_data = get_jwt()
    if jwt_data.get('role') != UserRole.ADMIN.value:
        return jsonify({"error": "Admin access required"}), 403
    
    data = request.json
    
    # Check required fields
    required_fields = ['name', 'points']
    for field in required_fields:
        if field not in data:
            return jsonify({"error": f"Missing required field: {field}"}), 400
    
    # Create achievement type
    achievement_type = AchievementType(
        name=data['name'],
        description=data.get('description', ''),
        icon=data.get('icon', ''),
        badge_image=data.get('badge_image', ''),
        points=data['points'],
        criteria=data.get('criteria', '{}')
    )
    
    db.session.add(achievement_type)
    db.session.commit()
    
    return jsonify(achievement_type.to_dict()), 201

@achievement_bp.route('/achievement-types/<int:achievement_type_id>', methods=['PUT'])
@jwt_required()
def update_achievement_type(achievement_type_id):
    """Update an achievement type (admin only)."""
    # Check if user is admin
    jwt_data = get_jwt()
    if jwt_data.get('role') != UserRole.ADMIN.value:
        return jsonify({"error": "Admin access required"}), 403
    
    achievement_type = AchievementType.query.get_or_404(achievement_type_id)
    data = request.json
    
    # Update fields
    if 'name' in data:
        achievement_type.name = data['name']
    if 'description' in data:
        achievement_type.description = data['description']
    if 'icon' in data:
        achievement_type.icon = data['icon']
    if 'badge_image' in data:
        achievement_type.badge_image = data['badge_image']
    if 'points' in data:
        achievement_type.points = data['points']
    if 'criteria' in data:
        achievement_type.criteria = data['criteria']
    
    db.session.commit()
    
    return jsonify(achievement_type.to_dict())

@achievement_bp.route('/achievement-types/<int:achievement_type_id>', methods=['DELETE'])
@jwt_required()
def delete_achievement_type(achievement_type_id):
    """Delete an achievement type (admin only)."""
    # Check if user is admin
    jwt_data = get_jwt()
    if jwt_data.get('role') != UserRole.ADMIN.value:
        return jsonify({"error": "Admin access required"}), 403
    
    achievement_type = AchievementType.query.get_or_404(achievement_type_id)
    db.session.delete(achievement_type)
    db.session.commit()
    
    return '', 204

# Achievement routes
@achievement_bp.route('/children/<int:child_id>/achievements', methods=['GET'])
@jwt_required()
def get_achievements(child_id):
    """Get all achievements for a child."""
    # Check access
    user_id = get_jwt_identity()
    user_role = get_jwt().get('role')
    
    if not check_child_access(child_id, user_id, user_role):
        return jsonify({"error": "Access denied"}), 403
    
    achievements = Achievement.query.filter_by(child_id=child_id).all()
    return jsonify([achievement.to_dict() for achievement in achievements])

@achievement_bp.route('/children/<int:child_id>/achievements', methods=['POST'])
@jwt_required()
def award_achievement(child_id):
    """Award an achievement to a child."""
    # Check access (only admin or parent can award achievements)
    user_id = get_jwt_identity()
    user_role = get_jwt().get('role')
    
    if user_role not in [UserRole.ADMIN.value, UserRole.PARENT.value]:
        return jsonify({"error": "Access denied"}), 403
    
    if user_role == UserRole.PARENT.value:
        # Check if parent has access to this child
        child = ChildProfile.query.get_or_404(child_id)
        if not child.parent or child.parent.user_id != user_id:
            return jsonify({"error": "Access denied"}), 403
    
    data = request.json
    
    # Check required fields
    if 'achievement_type_id' not in data:
        return jsonify({"error": "Missing required field: achievement_type_id"}), 400
    
    # Check if achievement type exists
    achievement_type = AchievementType.query.get_or_404(data['achievement_type_id'])
    
    # Check if child already has this achievement
    existing_achievement = Achievement.query.filter_by(
        child_id=child_id,
        achievement_type_id=achievement_type.id
    ).first()
    
    if existing_achievement:
        return jsonify({"error": "Child already has this achievement"}), 400
    
    # Award achievement
    achievement = Achievement(
        child_id=child_id,
        achievement_type_id=achievement_type.id,
        viewed=False
    )
    
    db.session.add(achievement)
    db.session.commit()
    
    return jsonify(achievement.to_dict()), 201

@achievement_bp.route('/children/<int:child_id>/achievements/<int:achievement_id>/view', methods=['PUT'])
@jwt_required()
def mark_achievement_viewed(child_id, achievement_id):
    """Mark an achievement as viewed."""
    # Check access
    user_id = get_jwt_identity()
    user_role = get_jwt().get('role')
    
    if not check_child_access(child_id, user_id, user_role):
        return jsonify({"error": "Access denied"}), 403
    
    # Get achievement
    achievement = Achievement.query.get_or_404(achievement_id)
    
    # Check if achievement belongs to the child
    if achievement.child_id != child_id:
        return jsonify({"error": "Achievement does not belong to this child"}), 403
    
    # Mark as viewed
    achievement.viewed = True
    db.session.commit()
    
    return jsonify(achievement.to_dict())

# Reward routes
@achievement_bp.route('/rewards', methods=['GET'])
def get_rewards():
    """Get all available rewards."""
    rewards = Reward.query.filter_by(is_active=True).all()
    return jsonify([reward.to_dict() for reward in rewards])

@achievement_bp.route('/rewards/<int:reward_id>', methods=['GET'])
def get_reward(reward_id):
    """Get a specific reward."""
    reward = Reward.query.get_or_404(reward_id)
    return jsonify(reward.to_dict())

@achievement_bp.route('/rewards', methods=['POST'])
@jwt_required()
def create_reward():
    """Create a new reward (admin only)."""
    # Check if user is admin
    jwt_data = get_jwt()
    if jwt_data.get('role') != UserRole.ADMIN.value:
        return jsonify({"error": "Admin access required"}), 403
    
    data = request.json
    
    # Check required fields
    required_fields = ['name', 'points_required']
    for field in required_fields:
        if field not in data:
            return jsonify({"error": f"Missing required field: {field}"}), 400
    
    # Create reward
    reward = Reward(
        name=data['name'],
        description=data.get('description', ''),
        image=data.get('image', ''),
        points_required=data['points_required'],
        is_active=data.get('is_active', True)
    )
    
    db.session.add(reward)
    db.session.commit()
    
    return jsonify(reward.to_dict()), 201

@achievement_bp.route('/rewards/<int:reward_id>', methods=['PUT'])
@jwt_required()
def update_reward(reward_id):
    """Update a reward (admin only)."""
    # Check if user is admin
    jwt_data = get_jwt()
    if jwt_data.get('role') != UserRole.ADMIN.value:
        return jsonify({"error": "Admin access required"}), 403
    
    reward = Reward.query.get_or_404(reward_id)
    data = request.json
    
    # Update fields
    if 'name' in data:
        reward.name = data['name']
    if 'description' in data:
        reward.description = data['description']
    if 'image' in data:
        reward.image = data['image']
    if 'points_required' in data:
        reward.points_required = data['points_required']
    if 'is_active' in data:
        reward.is_active = data['is_active']
    
    db.session.commit()
    
    return jsonify(reward.to_dict())

@achievement_bp.route('/rewards/<int:reward_id>', methods=['DELETE'])
@jwt_required()
def delete_reward(reward_id):
    """Delete a reward (admin only)."""
    # Check if user is admin
    jwt_data = get_jwt()
    if jwt_data.get('role') != UserRole.ADMIN.value:
        return jsonify({"error": "Admin access required"}), 403
    
    reward = Reward.query.get_or_404(reward_id)
    db.session.delete(reward)
    db.session.commit()
    
    return '', 204

# Child reward routes
@achievement_bp.route('/children/<int:child_id>/rewards', methods=['GET'])
@jwt_required()
def get_child_rewards(child_id):
    """Get all rewards for a child."""
    # Check access
    user_id = get_jwt_identity()
    user_role = get_jwt().get('role')
    
    if not check_child_access(child_id, user_id, user_role):
        return jsonify({"error": "Access denied"}), 403
    
    child_rewards = ChildReward.query.filter_by(child_id=child_id).all()
    return jsonify([child_reward.to_dict() for child_reward in child_rewards])

@achievement_bp.route('/children/<int:child_id>/rewards', methods=['POST'])
@jwt_required()
def redeem_reward(child_id):
    """Redeem a reward for a child."""
    # Check access
    user_id = get_jwt_identity()
    user_role = get_jwt().get('role')
    
    if not check_child_access(child_id, user_id, user_role):
        return jsonify({"error": "Access denied"}), 403
    
    data = request.json
    
    # Check required fields
    if 'reward_id' not in data:
        return jsonify({"error": "Missing required field: reward_id"}), 400
    
    # Check if reward exists and is active
    reward = Reward.query.get_or_404(data['reward_id'])
    if not reward.is_active:
        return jsonify({"error": "Reward is not active"}), 400
    
    # Calculate total points earned by the child
    total_points = db.session.query(db.func.sum(AchievementType.points)).join(
        Achievement, Achievement.achievement_type_id == AchievementType.id
    ).filter(Achievement.child_id == child_id).scalar() or 0
    
    # Calculate points already spent on rewards
    spent_points = db.session.query(db.func.sum(Reward.points_required)).join(
        ChildReward, ChildReward.reward_id == Reward.id
    ).filter(ChildReward.child_id == child_id).scalar() or 0
    
    # Calculate available points
    available_points = total_points - spent_points
    
    # Check if child has enough points
    if available_points < reward.points_required:
        return jsonify({
            "error": "Not enough points",
            "available_points": available_points,
            "required_points": reward.points_required
        }), 400
    
    # Redeem reward
    child_reward = ChildReward(
        child_id=child_id,
        reward_id=reward.id,
        redeemed=False
    )
    
    db.session.add(child_reward)
    db.session.commit()
    
    return jsonify(child_reward.to_dict()), 201

@achievement_bp.route('/children/<int:child_id>/rewards/<int:child_reward_id>/redeem', methods=['PUT'])
@jwt_required()
def mark_reward_redeemed(child_id, child_reward_id):
    """Mark a reward as redeemed."""
    # Check access (only admin or parent can mark rewards as redeemed)
    user_id = get_jwt_identity()
    user_role = get_jwt().get('role')
    
    if user_role not in [UserRole.ADMIN.value, UserRole.PARENT.value]:
        return jsonify({"error": "Access denied"}), 403
    
    if user_role == UserRole.PARENT.value:
        # Check if parent has access to this child
        child = ChildProfile.query.get_or_404(child_id)
        if not child.parent or child.parent.user_id != user_id:
            return jsonify({"error": "Access denied"}), 403
    
    # Get child reward
    child_reward = ChildReward.query.get_or_404(child_reward_id)
    
    # Check if child reward belongs to the child
    if child_reward.child_id != child_id:
        return jsonify({"error": "Reward does not belong to this child"}), 403
    
    # Check if already redeemed
    if child_reward.redeemed:
        return jsonify({"error": "Reward already redeemed"}), 400
    
    # Mark as redeemed
    child_reward.redeemed = True
    child_reward.redeemed_at = db.func.now()
    db.session.commit()
    
    return jsonify(child_reward.to_dict())

