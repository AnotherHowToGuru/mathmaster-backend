"""
Curriculum seed data for MathMaster application.
This file contains sample curriculum content aligned with the UK National Curriculum for Mathematics.
"""

import json
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from flask import Flask
from src.models import db, Topic, Lesson, Exercise

# Sample curriculum data
curriculum_data = {
    "year_1": {
        "topics": [
            {
                "name": "Numbers to 10",
                "description": "Learning to count, read, write, and compare numbers up to 10.",
                "icon": "numbers_10.png",
                "order": 1,
                "lessons": [
                    {
                        "title": "Counting to 10",
                        "description": "Learn to count objects up to 10.",
                        "content": json.dumps({
                            "slides": [
                                {
                                    "type": "introduction",
                                    "title": "Counting to 10",
                                    "content": "Today we're going to learn how to count objects up to 10. Counting is an important skill that helps us know how many things we have."
                                },
                                {
                                    "type": "example",
                                    "title": "Counting Objects",
                                    "content": "Let's count these apples together. Point to each apple as we count: 1, 2, 3, 4, 5.",
                                    "image": "counting_apples.png"
                                },
                                {
                                    "type": "interactive",
                                    "title": "Your Turn",
                                    "content": "Now you try! Count these stars.",
                                    "image": "counting_stars.png",
                                    "answer": "7"
                                }
                            ]
                        }),
                        "order": 1,
                        "difficulty": 1,
                        "estimated_time": 10,
                        "exercises": [
                            {
                                "title": "Count the Apples",
                                "description": "Count how many apples are shown.",
                                "question_type": "multiple_choice",
                                "question_data": json.dumps({
                                    "question": "How many apples are there?",
                                    "image": "exercise_apples.png",
                                    "options": ["5", "6", "7", "8"]
                                }),
                                "answer_data": json.dumps({
                                    "correct_answer": "6",
                                    "explanation": "There are 6 apples in the picture. We count them one by one: 1, 2, 3, 4, 5, 6."
                                }),
                                "difficulty": 1,
                                "order": 1
                            },
                            {
                                "title": "Count the Stars",
                                "description": "Count how many stars are shown.",
                                "question_type": "multiple_choice",
                                "question_data": json.dumps({
                                    "question": "How many stars are there?",
                                    "image": "exercise_stars.png",
                                    "options": ["7", "8", "9", "10"]
                                }),
                                "answer_data": json.dumps({
                                    "correct_answer": "8",
                                    "explanation": "There are 8 stars in the picture. We count them one by one: 1, 2, 3, 4, 5, 6, 7, 8."
                                }),
                                "difficulty": 1,
                                "order": 2
                            },
                            {
                                "title": "Match Numbers to Objects",
                                "description": "Match the number to the correct group of objects.",
                                "question_type": "matching",
                                "question_data": json.dumps({
                                    "question": "Match each number to the correct group of objects.",
                                    "pairs": [
                                        {"id": 1, "left": "3", "right": "exercise_3_balls.png"},
                                        {"id": 2, "left": "5", "right": "exercise_5_pencils.png"},
                                        {"id": 3, "left": "7", "right": "exercise_7_flowers.png"}
                                    ]
                                }),
                                "answer_data": json.dumps({
                                    "correct_pairs": [
                                        {"left": "3", "right": "exercise_3_balls.png"},
                                        {"left": "5", "right": "exercise_5_pencils.png"},
                                        {"left": "7", "right": "exercise_7_flowers.png"}
                                    ],
                                    "explanation": "3 matches with 3 balls, 5 matches with 5 pencils, and 7 matches with 7 flowers."
                                }),
                                "difficulty": 2,
                                "order": 3
                            }
                        ]
                    },
                    {
                        "title": "Reading and Writing Numbers to 10",
                        "description": "Learn to read and write numbers up to 10.",
                        "content": json.dumps({
                            "slides": [
                                {
                                    "type": "introduction",
                                    "title": "Reading and Writing Numbers",
                                    "content": "Now that we can count objects, let's learn how to read and write the numbers from 1 to 10."
                                },
                                {
                                    "type": "example",
                                    "title": "Number 1",
                                    "content": "This is the number 1. It looks like a straight line. We say 'one'.",
                                    "image": "number_1.png"
                                },
                                {
                                    "type": "example",
                                    "title": "Number 2",
                                    "content": "This is the number 2. It has a curve and a flat bottom. We say 'two'.",
                                    "image": "number_2.png"
                                },
                                {
                                    "type": "interactive",
                                    "title": "Your Turn",
                                    "content": "What number is this?",
                                    "image": "number_5.png",
                                    "answer": "5"
                                }
                            ]
                        }),
                        "order": 2,
                        "difficulty": 1,
                        "estimated_time": 15,
                        "exercises": [
                            {
                                "title": "Identify Numbers",
                                "description": "Identify the numbers shown.",
                                "question_type": "multiple_choice",
                                "question_data": json.dumps({
                                    "question": "What number is this?",
                                    "image": "exercise_number_4.png",
                                    "options": ["2", "3", "4", "5"]
                                }),
                                "answer_data": json.dumps({
                                    "correct_answer": "4",
                                    "explanation": "This is the number 4. It has a straight line down, a line across, and another line down."
                                }),
                                "difficulty": 1,
                                "order": 1
                            },
                            {
                                "title": "Write Numbers",
                                "description": "Select the correct written form of numbers.",
                                "question_type": "multiple_choice",
                                "question_data": json.dumps({
                                    "question": "How do we write the number 'seven'?",
                                    "options": ["5", "6", "7", "8"]
                                }),
                                "answer_data": json.dumps({
                                    "correct_answer": "7",
                                    "explanation": "The word 'seven' is written as the number 7."
                                }),
                                "difficulty": 1,
                                "order": 2
                            },
                            {
                                "title": "Match Numbers to Words",
                                "description": "Match the number to its written word.",
                                "question_type": "matching",
                                "question_data": json.dumps({
                                    "question": "Match each number to its word.",
                                    "pairs": [
                                        {"id": 1, "left": "3", "right": "three"},
                                        {"id": 2, "left": "6", "right": "six"},
                                        {"id": 3, "left": "9", "right": "nine"}
                                    ]
                                }),
                                "answer_data": json.dumps({
                                    "correct_pairs": [
                                        {"left": "3", "right": "three"},
                                        {"left": "6", "right": "six"},
                                        {"left": "9", "right": "nine"}
                                    ],
                                    "explanation": "3 is written as 'three', 6 is written as 'six', and 9 is written as 'nine'."
                                }),
                                "difficulty": 2,
                                "order": 3
                            }
                        ]
                    }
                ]
            },
            {
                "name": "Addition and Subtraction within 10",
                "description": "Learning to add and subtract numbers within 10.",
                "icon": "addition_subtraction.png",
                "order": 2,
                "lessons": [
                    {
                        "title": "Adding Numbers to 10",
                        "description": "Learn to add numbers with a sum up to 10.",
                        "content": json.dumps({
                            "slides": [
                                {
                                    "type": "introduction",
                                    "title": "Adding Numbers",
                                    "content": "Addition means combining groups of objects to find the total. We use the + sign for addition."
                                },
                                {
                                    "type": "example",
                                    "title": "Adding with Objects",
                                    "content": "If we have 2 apples and get 3 more apples, we can add them: 2 + 3 = 5. We now have 5 apples in total.",
                                    "image": "adding_apples.png"
                                },
                                {
                                    "type": "interactive",
                                    "title": "Your Turn",
                                    "content": "How many flowers are there in total?",
                                    "image": "adding_flowers.png",
                                    "answer": "7"
                                }
                            ]
                        }),
                        "order": 1,
                        "difficulty": 2,
                        "estimated_time": 15,
                        "exercises": [
                            {
                                "title": "Add with Pictures",
                                "description": "Add the number of objects shown.",
                                "question_type": "multiple_choice",
                                "question_data": json.dumps({
                                    "question": "How many fruits are there in total?",
                                    "image": "exercise_add_fruits.png",
                                    "options": ["5", "6", "7", "8"]
                                }),
                                "answer_data": json.dumps({
                                    "correct_answer": "7",
                                    "explanation": "There are 4 apples and 3 oranges. 4 + 3 = 7 fruits in total."
                                }),
                                "difficulty": 2,
                                "order": 1
                            },
                            {
                                "title": "Simple Addition",
                                "description": "Solve simple addition problems.",
                                "question_type": "multiple_choice",
                                "question_data": json.dumps({
                                    "question": "What is 3 + 5?",
                                    "options": ["7", "8", "9", "10"]
                                }),
                                "answer_data": json.dumps({
                                    "correct_answer": "8",
                                    "explanation": "3 + 5 = 8. We can count up: 3, then 4, 5, 6, 7, 8."
                                }),
                                "difficulty": 2,
                                "order": 2
                            },
                            {
                                "title": "Fill in the Missing Number",
                                "description": "Find the missing number in addition equations.",
                                "question_type": "fill_blank",
                                "question_data": json.dumps({
                                    "question": "4 + ___ = 9",
                                    "image": "exercise_missing_number.png"
                                }),
                                "answer_data": json.dumps({
                                    "correct_answer": "5",
                                    "explanation": "4 + 5 = 9. We need to add 5 to 4 to get 9."
                                }),
                                "difficulty": 3,
                                "order": 3
                            }
                        ]
                    },
                    {
                        "title": "Subtracting Numbers within 10",
                        "description": "Learn to subtract numbers within 10.",
                        "content": json.dumps({
                            "slides": [
                                {
                                    "type": "introduction",
                                    "title": "Subtracting Numbers",
                                    "content": "Subtraction means taking away objects from a group. We use the - sign for subtraction."
                                },
                                {
                                    "type": "example",
                                    "title": "Subtracting with Objects",
                                    "content": "If we have 7 balloons and 3 pop, we can subtract: 7 - 3 = 4. We have 4 balloons left.",
                                    "image": "subtracting_balloons.png"
                                },
                                {
                                    "type": "interactive",
                                    "title": "Your Turn",
                                    "content": "There were 8 birds on a tree. 5 flew away. How many birds are left?",
                                    "image": "subtracting_birds.png",
                                    "answer": "3"
                                }
                            ]
                        }),
                        "order": 2,
                        "difficulty": 2,
                        "estimated_time": 15,
                        "exercises": [
                            {
                                "title": "Subtract with Pictures",
                                "description": "Subtract the number of objects shown.",
                                "question_type": "multiple_choice",
                                "question_data": json.dumps({
                                    "question": "There were 9 cookies. Some were eaten. How many cookies are left?",
                                    "image": "exercise_subtract_cookies.png",
                                    "options": ["3", "4", "5", "6"]
                                }),
                                "answer_data": json.dumps({
                                    "correct_answer": "4",
                                    "explanation": "There were 9 cookies, and 5 were eaten. 9 - 5 = 4 cookies left."
                                }),
                                "difficulty": 2,
                                "order": 1
                            },
                            {
                                "title": "Simple Subtraction",
                                "description": "Solve simple subtraction problems.",
                                "question_type": "multiple_choice",
                                "question_data": json.dumps({
                                    "question": "What is 8 - 3?",
                                    "options": ["3", "4", "5", "6"]
                                }),
                                "answer_data": json.dumps({
                                    "correct_answer": "5",
                                    "explanation": "8 - 3 = 5. We can count down: 8, then 7, 6, 5."
                                }),
                                "difficulty": 2,
                                "order": 2
                            },
                            {
                                "title": "Fill in the Missing Number",
                                "description": "Find the missing number in subtraction equations.",
                                "question_type": "fill_blank",
                                "question_data": json.dumps({
                                    "question": "10 - ___ = 6",
                                    "image": "exercise_missing_number_subtraction.png"
                                }),
                                "answer_data": json.dumps({
                                    "correct_answer": "4",
                                    "explanation": "10 - 4 = 6. We need to subtract 4 from 10 to get 6."
                                }),
                                "difficulty": 3,
                                "order": 3
                            }
                        ]
                    }
                ]
            }
        ]
    },
    "year_2": {
        "topics": [
            {
                "name": "Place Value",
                "description": "Understanding the value of each digit in a two-digit number.",
                "icon": "place_value.png",
                "order": 1,
                "lessons": [
                    {
                        "title": "Tens and Ones",
                        "description": "Learn about tens and ones in two-digit numbers.",
                        "content": json.dumps({
                            "slides": [
                                {
                                    "type": "introduction",
                                    "title": "Tens and Ones",
                                    "content": "Two-digit numbers have two places: tens and ones. The first digit tells us how many tens, and the second digit tells us how many ones."
                                },
                                {
                                    "type": "example",
                                    "title": "Understanding Place Value",
                                    "content": "In the number 37, the 3 is in the tens place, so it means 3 tens or 30. The 7 is in the ones place, so it means 7 ones. 30 + 7 = 37.",
                                    "image": "place_value_37.png"
                                },
                                {
                                    "type": "interactive",
                                    "title": "Your Turn",
                                    "content": "In the number 52, how many tens are there?",
                                    "image": "place_value_52.png",
                                    "answer": "5"
                                }
                            ]
                        }),
                        "order": 1,
                        "difficulty": 2,
                        "estimated_time": 20,
                        "exercises": [
                            {
                                "title": "Identify Tens and Ones",
                                "description": "Identify the tens and ones in two-digit numbers.",
                                "question_type": "multiple_choice",
                                "question_data": json.dumps({
                                    "question": "How many tens are in the number 64?",
                                    "options": ["4", "6", "10", "60"]
                                }),
                                "answer_data": json.dumps({
                                    "correct_answer": "6",
                                    "explanation": "In 64, the 6 is in the tens place, so there are 6 tens."
                                }),
                                "difficulty": 2,
                                "order": 1
                            },
                            {
                                "title": "Represent Numbers with Base-10 Blocks",
                                "description": "Match numbers to their representation with base-10 blocks.",
                                "question_type": "multiple_choice",
                                "question_data": json.dumps({
                                    "question": "Which base-10 blocks show the number 43?",
                                    "image": "exercise_base10_options.png",
                                    "options": ["A", "B", "C", "D"]
                                }),
                                "answer_data": json.dumps({
                                    "correct_answer": "C",
                                    "explanation": "The number 43 is represented by 4 tens (rods) and 3 ones (cubes)."
                                }),
                                "difficulty": 2,
                                "order": 2
                            },
                            {
                                "title": "Write Numbers in Expanded Form",
                                "description": "Write two-digit numbers in expanded form.",
                                "question_type": "multiple_choice",
                                "question_data": json.dumps({
                                    "question": "What is 78 in expanded form?",
                                    "options": ["7 + 8", "70 + 8", "7 + 80", "78 + 0"]
                                }),
                                "answer_data": json.dumps({
                                    "correct_answer": "70 + 8",
                                    "explanation": "78 in expanded form is 70 + 8, which is 7 tens + 8 ones."
                                }),
                                "difficulty": 3,
                                "order": 3
                            }
                        ]
                    }
                ]
            }
        ]
    }
}

def seed_curriculum():
    """Seed the database with curriculum data."""
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = f"mysql+pymysql://{os.getenv('DB_USERNAME', 'root')}:{os.getenv('DB_PASSWORD', 'password')}@{os.getenv('DB_HOST', 'localhost')}:{os.getenv('DB_PORT', '3306')}/{os.getenv('DB_NAME', 'mathmaster_db')}"
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.init_app(app)
    
    with app.app_context():
        # Clear existing data
        Exercise.query.delete()
        Lesson.query.delete()
        Topic.query.delete()
        
        # Seed topics, lessons, and exercises
        for year_group, year_data in curriculum_data.items():
            year_number = int(year_group.split('_')[1])
            
            for topic_data in year_data['topics']:
                # Create topic
                topic = Topic(
                    name=topic_data['name'],
                    description=topic_data['description'],
                    icon=topic_data['icon'],
                    year_group=year_number,
                    order=topic_data['order']
                )
                db.session.add(topic)
                db.session.flush()  # Flush to get the topic ID
                
                for lesson_data in topic_data['lessons']:
                    # Create lesson
                    lesson = Lesson(
                        topic_id=topic.id,
                        title=lesson_data['title'],
                        description=lesson_data['description'],
                        content=lesson_data['content'],
                        order=lesson_data['order'],
                        difficulty=lesson_data['difficulty'],
                        estimated_time=lesson_data.get('estimated_time')
                    )
                    db.session.add(lesson)
                    db.session.flush()  # Flush to get the lesson ID
                    
                    for exercise_data in lesson_data['exercises']:
                        # Create exercise
                        exercise = Exercise(
                            lesson_id=lesson.id,
                            title=exercise_data['title'],
                            description=exercise_data['description'],
                            question_type=exercise_data['question_type'],
                            question_data=exercise_data['question_data'],
                            answer_data=exercise_data['answer_data'],
                            difficulty=exercise_data['difficulty'],
                            order=exercise_data['order']
                        )
                        db.session.add(exercise)
        
        # Commit all changes
        db.session.commit()
        
        # Print summary
        topic_count = Topic.query.count()
        lesson_count = Lesson.query.count()
        exercise_count = Exercise.query.count()
        
        print(f"Seeded {topic_count} topics, {lesson_count} lessons, and {exercise_count} exercises.")

if __name__ == '__main__':
    seed_curriculum()

