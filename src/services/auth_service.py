from flask_bcrypt import Bcrypt
from flask_jwt_extended import create_access_token, create_refresh_token
from datetime import datetime, timedelta
from src.models import User, UserRole, ParentProfile, ChildProfile, db
import re

bcrypt = Bcrypt()

class AuthService:
    @staticmethod
    def hash_password(password):
        """Hash a password for storing."""
        return bcrypt.generate_password_hash(password).decode('utf-8')
    
    @staticmethod
    def check_password(hashed_password, password):
        """Check hashed password against user password."""
        return bcrypt.check_password_hash(hashed_password, password)
    
    @staticmethod
    def validate_email(email):
        """Validate email format."""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None
    
    @staticmethod
    def validate_password(password):
        """
        Validate password strength.
        Password must be at least 8 characters long and contain at least one uppercase letter,
        one lowercase letter, one number, and one special character.
        """
        if len(password) < 8:
            return False, "Password must be at least 8 characters long"
        
        if not re.search(r'[A-Z]', password):
            return False, "Password must contain at least one uppercase letter"
        
        if not re.search(r'[a-z]', password):
            return False, "Password must contain at least one lowercase letter"
        
        if not re.search(r'[0-9]', password):
            return False, "Password must contain at least one number"
        
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            return False, "Password must contain at least one special character"
        
        return True, "Password is valid"
    
    @staticmethod
    def register_parent(username, email, password, first_name=None, last_name=None, phone_number=None):
        """Register a new parent user."""
        # Check if username or email already exists
        if User.query.filter_by(username=username).first():
            return False, "Username already exists"
        
        if User.query.filter_by(email=email).first():
            return False, "Email already exists"
        
        # Validate email format
        if not AuthService.validate_email(email):
            return False, "Invalid email format"
        
        # Validate password strength
        is_valid, message = AuthService.validate_password(password)
        if not is_valid:
            return False, message
        
        # Create user
        hashed_password = AuthService.hash_password(password)
        user = User(
            username=username,
            email=email,
            password_hash=hashed_password,
            role=UserRole.PARENT
        )
        
        # Create parent profile
        parent_profile = ParentProfile(
            user=user,
            first_name=first_name,
            last_name=last_name,
            phone_number=phone_number
        )
        
        # Save to database
        db.session.add(user)
        db.session.add(parent_profile)
        db.session.commit()
        
        return True, user
    
    @staticmethod
    def register_child(parent_id, username, first_name, year_group, avatar=None, date_of_birth=None):
        """Register a new child user linked to a parent."""
        # Check if parent exists
        parent_profile = ParentProfile.query.get(parent_id)
        if not parent_profile:
            return False, "Parent not found"
        
        # Check if username already exists
        if User.query.filter_by(username=username).first():
            return False, "Username already exists"
        
        # Generate a simple password for the child account (can be changed later)
        password = f"Child{username}123!"
        hashed_password = AuthService.hash_password(password)
        
        # Create user with a generated email based on parent's email
        parent_email = parent_profile.user.email
        email_parts = parent_email.split('@')
        child_email = f"{email_parts[0]}+{username}@{email_parts[1]}"
        
        user = User(
            username=username,
            email=child_email,
            password_hash=hashed_password,
            role=UserRole.CHILD
        )
        
        # Create child profile
        child_profile = ChildProfile(
            user=user,
            parent=parent_profile,
            first_name=first_name,
            avatar=avatar or "default_avatar.png",
            year_group=year_group,
            date_of_birth=date_of_birth
        )
        
        # Save to database
        db.session.add(user)
        db.session.add(child_profile)
        db.session.commit()
        
        return True, user
    
    @staticmethod
    def login(username_or_email, password):
        """Authenticate a user and return tokens."""
        # Check if input is email or username
        if '@' in username_or_email:
            user = User.query.filter_by(email=username_or_email).first()
        else:
            user = User.query.filter_by(username=username_or_email).first()
        
        if not user:
            return False, "User not found"
        
        if not AuthService.check_password(user.password_hash, password):
            return False, "Invalid password"
        
        # Create tokens
        access_token = create_access_token(
            identity=user.id,
            additional_claims={"role": user.role.value}
        )
        refresh_token = create_refresh_token(identity=user.id)
        
        return True, {
            "user": user.to_dict(),
            "access_token": access_token,
            "refresh_token": refresh_token
        }
    
    @staticmethod
    def refresh_token(user_id):
        """Generate a new access token from a refresh token."""
        user = User.query.get(user_id)
        if not user:
            return False, "User not found"
        
        access_token = create_access_token(
            identity=user.id,
            additional_claims={"role": user.role.value}
        )
        
        return True, {"access_token": access_token}

