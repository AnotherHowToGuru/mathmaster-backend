from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from src.services.auth_service import AuthService
from src.models import User, UserRole, ParentProfile, ChildProfile

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register/parent', methods=['POST'])
def register_parent():
    """Register a new parent user."""
    data = request.json
    
    # Check required fields
    required_fields = ['username', 'email', 'password']
    for field in required_fields:
        if field not in data:
            return jsonify({"error": f"Missing required field: {field}"}), 400
    
    # Register parent
    success, result = AuthService.register_parent(
        username=data['username'],
        email=data['email'],
        password=data['password'],
        first_name=data.get('first_name'),
        last_name=data.get('last_name'),
        phone_number=data.get('phone_number')
    )
    
    if not success:
        return jsonify({"error": result}), 400
    
    return jsonify({"message": "Parent registered successfully", "user_id": result.id}), 201

@auth_bp.route('/register/child', methods=['POST'])
@jwt_required()
def register_child():
    """Register a new child user (requires parent authentication)."""
    # Check if the authenticated user is a parent
    jwt_data = get_jwt()
    if jwt_data.get('role') != UserRole.PARENT.value:
        return jsonify({"error": "Only parents can register children"}), 403
    
    # Get parent ID
    parent_user_id = get_jwt_identity()
    parent_profile = ParentProfile.query.filter_by(user_id=parent_user_id).first()
    if not parent_profile:
        return jsonify({"error": "Parent profile not found"}), 404
    
    data = request.json
    
    # Check required fields
    required_fields = ['username', 'first_name', 'year_group']
    for field in required_fields:
        if field not in data:
            return jsonify({"error": f"Missing required field: {field}"}), 400
    
    # Register child
    success, result = AuthService.register_child(
        parent_id=parent_profile.id,
        username=data['username'],
        first_name=data['first_name'],
        year_group=data['year_group'],
        avatar=data.get('avatar'),
        date_of_birth=data.get('date_of_birth')
    )
    
    if not success:
        return jsonify({"error": result}), 400
    
    return jsonify({"message": "Child registered successfully", "user_id": result.id}), 201

@auth_bp.route('/login', methods=['POST'])
def login():
    """Authenticate a user and return tokens."""
    data = request.json
    
    # Check required fields
    if 'username_or_email' not in data or 'password' not in data:
        return jsonify({"error": "Missing username/email or password"}), 400
    
    # Login
    success, result = AuthService.login(
        username_or_email=data['username_or_email'],
        password=data['password']
    )
    
    if not success:
        return jsonify({"error": result}), 401
    
    return jsonify(result), 200

@auth_bp.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh():
    """Refresh access token."""
    user_id = get_jwt_identity()
    success, result = AuthService.refresh_token(user_id)
    
    if not success:
        return jsonify({"error": result}), 401
    
    return jsonify(result), 200

@auth_bp.route('/me', methods=['GET'])
@jwt_required()
def get_current_user():
    """Get current authenticated user."""
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    
    if not user:
        return jsonify({"error": "User not found"}), 404
    
    # Get profile based on role
    profile = None
    if user.role == UserRole.PARENT:
        profile = ParentProfile.query.filter_by(user_id=user.id).first()
        if profile:
            profile = profile.to_dict()
    elif user.role == UserRole.CHILD:
        profile = ChildProfile.query.filter_by(user_id=user.id).first()
        if profile:
            profile = profile.to_dict()
    
    return jsonify({
        "user": user.to_dict(),
        "profile": profile
    }), 200

