# MathMaster Backend API

This is the backend API for the MathMaster UK Primary School Math Tutor application. It provides endpoints for user authentication, curriculum content, progress tracking, achievements, and subscription management.

## Table of Contents

- [Setup](#setup)
- [Environment Variables](#environment-variables)
- [API Documentation](#api-documentation)
- [Database Schema](#database-schema)
- [Deployment](#deployment)

## Setup

### Prerequisites

- Python 3.8+
- MySQL database
- Stripe account (for subscription management)

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/mathmaster-backend.git
   cd mathmaster-backend
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Set up environment variables (see [Environment Variables](#environment-variables) section).

5. Initialize the database:
   ```bash
   python src/main.py
   ```

6. Run the development server:
   ```bash
   python src/main.py
   ```

The API will be available at `http://localhost:5000`.

## Environment Variables

Create a `.env` file in the root directory with the following variables:

```
# Database Configuration
DB_USERNAME=root
DB_PASSWORD=password
DB_HOST=localhost
DB_PORT=3306
DB_NAME=mathmaster_db

# Security
SECRET_KEY=your_secret_key
JWT_SECRET_KEY=your_jwt_secret_key

# Stripe Configuration
STRIPE_SECRET_KEY=your_stripe_secret_key
STRIPE_WEBHOOK_SECRET=your_stripe_webhook_secret
```

## API Documentation

### Authentication

#### Register Parent

- **URL**: `/api/auth/register/parent`
- **Method**: `POST`
- **Auth Required**: No
- **Body**:
  ```json
  {
    "username": "parent_user",
    "email": "parent@example.com",
    "password": "SecurePassword123!",
    "first_name": "John",
    "last_name": "Doe",
    "phone_number": "1234567890"
  }
  ```
- **Success Response**: `201 Created`
  ```json
  {
    "message": "Parent registered successfully",
    "user_id": 1
  }
  ```

#### Register Child

- **URL**: `/api/auth/register/child`
- **Method**: `POST`
- **Auth Required**: Yes (Parent token)
- **Body**:
  ```json
  {
    "username": "child_user",
    "first_name": "Jane",
    "year_group": 3,
    "avatar": "fox.png",
    "date_of_birth": "2015-05-15"
  }
  ```
- **Success Response**: `201 Created`
  ```json
  {
    "message": "Child registered successfully",
    "user_id": 2
  }
  ```

#### Login

- **URL**: `/api/auth/login`
- **Method**: `POST`
- **Auth Required**: No
- **Body**:
  ```json
  {
    "username_or_email": "parent@example.com",
    "password": "SecurePassword123!"
  }
  ```
- **Success Response**: `200 OK`
  ```json
  {
    "user": {
      "id": 1,
      "username": "parent_user",
      "email": "parent@example.com",
      "role": "parent"
    },
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
  }
  ```

#### Refresh Token

- **URL**: `/api/auth/refresh`
- **Method**: `POST`
- **Auth Required**: Yes (Refresh token)
- **Success Response**: `200 OK`
  ```json
  {
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
  }
  ```

#### Get Current User

- **URL**: `/api/auth/me`
- **Method**: `GET`
- **Auth Required**: Yes
- **Success Response**: `200 OK`
  ```json
  {
    "user": {
      "id": 1,
      "username": "parent_user",
      "email": "parent@example.com",
      "role": "parent"
    },
    "profile": {
      "id": 1,
      "user_id": 1,
      "first_name": "John",
      "last_name": "Doe",
      "phone_number": "1234567890",
      "subscription_status": "free"
    }
  }
  ```

### Curriculum

#### Get Topics

- **URL**: `/api/curriculum/topics`
- **Method**: `GET`
- **Auth Required**: No
- **Query Parameters**:
  - `year_group` (optional): Filter topics by year group
- **Success Response**: `200 OK`
  ```json
  [
    {
      "id": 1,
      "name": "Numbers to 10",
      "description": "Learning to count and recognize numbers up to 10",
      "icon": "numbers.png",
      "year_group": 1,
      "order": 1,
      "lesson_count": 5
    }
  ]
  ```

#### Get Topic

- **URL**: `/api/curriculum/topics/{topic_id}`
- **Method**: `GET`
- **Auth Required**: No
- **Success Response**: `200 OK`
  ```json
  {
    "id": 1,
    "name": "Numbers to 10",
    "description": "Learning to count and recognize numbers up to 10",
    "icon": "numbers.png",
    "year_group": 1,
    "order": 1,
    "lesson_count": 5
  }
  ```

#### Get Lessons for Topic

- **URL**: `/api/curriculum/topics/{topic_id}/lessons`
- **Method**: `GET`
- **Auth Required**: No
- **Success Response**: `200 OK`
  ```json
  [
    {
      "id": 1,
      "topic_id": 1,
      "title": "Counting to 5",
      "description": "Learn to count objects up to 5",
      "content": "...",
      "order": 1,
      "difficulty": 1,
      "exercise_count": 3
    }
  ]
  ```

#### Get Lesson

- **URL**: `/api/curriculum/lessons/{lesson_id}`
- **Method**: `GET`
- **Auth Required**: No
- **Success Response**: `200 OK`
  ```json
  {
    "id": 1,
    "topic_id": 1,
    "title": "Counting to 5",
    "description": "Learn to count objects up to 5",
    "content": "...",
    "order": 1,
    "difficulty": 1,
    "exercise_count": 3
  }
  ```

#### Get Exercises for Lesson

- **URL**: `/api/curriculum/lessons/{lesson_id}/exercises`
- **Method**: `GET`
- **Auth Required**: No
- **Success Response**: `200 OK`
  ```json
  [
    {
      "id": 1,
      "lesson_id": 1,
      "title": "Count the Apples",
      "description": "Count how many apples are shown",
      "question_type": "multiple_choice",
      "question_data": "...",
      "difficulty": 1,
      "order": 1
    }
  ]
  ```

### Progress Tracking

#### Record Exercise Progress

- **URL**: `/api/progress/children/{child_id}/progress/exercises/{exercise_id}`
- **Method**: `POST`
- **Auth Required**: Yes
- **Body**:
  ```json
  {
    "score": 100,
    "time_spent": 60,
    "completed": true
  }
  ```
- **Success Response**: `201 Created`
  ```json
  {
    "id": 1,
    "child_id": 1,
    "exercise_id": 1,
    "score": 100,
    "time_spent": 60,
    "attempts": 1,
    "completed": true
  }
  ```

#### Update Lesson Progress

- **URL**: `/api/progress/children/{child_id}/progress/lessons/{lesson_id}`
- **Method**: `POST`
- **Auth Required**: Yes
- **Body**:
  ```json
  {
    "status": "in_progress",
    "progress_percentage": 50,
    "last_position": "slide_3",
    "time_spent": 120
  }
  ```
- **Success Response**: `200 OK`
  ```json
  {
    "id": 1,
    "child_id": 1,
    "lesson_id": 1,
    "status": "in_progress",
    "progress_percentage": 50,
    "last_position": "slide_3",
    "time_spent": 120
  }
  ```

#### Get Progress Summary

- **URL**: `/api/progress/children/{child_id}/summary`
- **Method**: `GET`
- **Auth Required**: Yes
- **Success Response**: `200 OK`
  ```json
  {
    "child_id": 1,
    "year_group": 1,
    "topics": {
      "total": 10,
      "completed": 2,
      "percentage": 20
    },
    "lessons": {
      "total": 50,
      "completed": 8,
      "percentage": 16
    },
    "exercises": {
      "total": 150,
      "completed": 25,
      "percentage": 16.67
    },
    "average_score": 85.5,
    "total_time_spent": 3600,
    "recent_activity": [...]
  }
  ```

### Achievements

#### Get Child Achievements

- **URL**: `/api/achievements/children/{child_id}/achievements`
- **Method**: `GET`
- **Auth Required**: Yes
- **Success Response**: `200 OK`
  ```json
  [
    {
      "id": 1,
      "child_id": 1,
      "achievement_type_id": 1,
      "earned_at": "2025-06-06T12:00:00Z",
      "viewed": false,
      "achievement_type": {
        "id": 1,
        "name": "First Lesson Completed",
        "description": "Completed your first lesson",
        "badge_image": "first_lesson.png",
        "points": 10
      }
    }
  ]
  ```

#### Award Achievement

- **URL**: `/api/achievements/children/{child_id}/achievements`
- **Method**: `POST`
- **Auth Required**: Yes (Admin or Parent)
- **Body**:
  ```json
  {
    "achievement_type_id": 1
  }
  ```
- **Success Response**: `201 Created`
  ```json
  {
    "id": 1,
    "child_id": 1,
    "achievement_type_id": 1,
    "earned_at": "2025-06-06T12:00:00Z",
    "viewed": false
  }
  ```

### Subscription Management

#### Get Subscription Plans

- **URL**: `/api/subscription/plans`
- **Method**: `GET`
- **Auth Required**: No
- **Success Response**: `200 OK`
  ```json
  [
    {
      "id": "price_1234567890",
      "product_id": "prod_1234567890",
      "name": "Monthly Subscription",
      "description": "Access to all content for one month",
      "amount": 9.99,
      "currency": "gbp",
      "interval": "month",
      "interval_count": 1
    }
  ]
  ```

#### Create Checkout Session

- **URL**: `/api/subscription/checkout-session`
- **Method**: `POST`
- **Auth Required**: Yes (Parent)
- **Body**:
  ```json
  {
    "price_id": "price_1234567890",
    "success_url": "https://example.com/success",
    "cancel_url": "https://example.com/cancel"
  }
  ```
- **Success Response**: `200 OK`
  ```json
  {
    "checkout_url": "https://checkout.stripe.com/..."
  }
  ```

#### Get Subscription Status

- **URL**: `/api/subscription/status`
- **Method**: `GET`
- **Auth Required**: Yes (Parent)
- **Success Response**: `200 OK`
  ```json
  {
    "status": "active",
    "expiry": "2025-07-06T12:00:00Z",
    "customer_id": "cus_1234567890"
  }
  ```

## Database Schema

The database schema consists of the following main tables:

- **users**: Stores user account information
- **parent_profiles**: Stores parent-specific information
- **child_profiles**: Stores child-specific information
- **topics**: Stores curriculum topics
- **lessons**: Stores lessons for each topic
- **exercises**: Stores exercises for each lesson
- **progress_records**: Tracks child progress on exercises
- **lesson_progress**: Tracks child progress on lessons
- **topic_progress**: Tracks child progress on topics
- **daily_activities**: Tracks daily usage statistics
- **achievement_types**: Defines available achievements
- **achievements**: Tracks achievements earned by children
- **rewards**: Defines available rewards
- **child_rewards**: Tracks rewards earned by children

## Deployment

### Heroku Deployment

1. Create a Heroku account and install the Heroku CLI
2. Login to Heroku:
   ```bash
   heroku login
   ```

3. Create a new Heroku app:
   ```bash
   heroku create mathmaster-api
   ```

4. Add a MySQL database:
   ```bash
   heroku addons:create jawsdb:kitefin
   ```

5. Set environment variables:
   ```bash
   heroku config:set SECRET_KEY=your_secret_key
   heroku config:set JWT_SECRET_KEY=your_jwt_secret_key
   heroku config:set STRIPE_SECRET_KEY=your_stripe_secret_key
   heroku config:set STRIPE_WEBHOOK_SECRET=your_stripe_webhook_secret
   ```

6. Deploy the application:
   ```bash
   git push heroku main
   ```

### AWS Deployment

1. Create an EC2 instance
2. Install required packages:
   ```bash
   sudo apt update
   sudo apt install python3-pip python3-venv mysql-server nginx
   ```

3. Clone the repository and set up the application
4. Configure Nginx as a reverse proxy
5. Set up SSL with Let's Encrypt
6. Configure the application to run with Gunicorn and Supervisor

## License

This project is licensed under the MIT License - see the LICENSE file for details.

