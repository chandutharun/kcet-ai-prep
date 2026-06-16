"""
SQLite database - STUDENT LOGIN + CHAT HISTORY
"""

import sqlite3
from datetime import datetime
from src.config import DATABASE_PATH


def init_database():
    """Initialize database"""
    conn = sqlite3.connect(DATABASE_PATH)
    c = conn.cursor()
    
    # Students table
    c.execute('''
        CREATE TABLE IF NOT EXISTS students (
            student_id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            email TEXT,
            target_score INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Chat history
    c.execute('''
        CREATE TABLE IF NOT EXISTS chat_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id TEXT,
            message_type TEXT,
            content TEXT,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Student progress
    c.execute('''
        CREATE TABLE IF NOT EXISTS student_progress (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id TEXT,
            chapter TEXT,
            subject TEXT,
            question TEXT,
            answer TEXT,
            time_spent INTEGER,
            understood BOOLEAN,
            difficulty TEXT,
            date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    conn.commit()
    conn.close()


def login_student(student_id: str, name: str):
    """Login student - Check if exists"""
    conn = sqlite3.connect(DATABASE_PATH)
    c = conn.cursor()
    
    # Check if student exists
    c.execute('SELECT name, email FROM students WHERE student_id = ?', (student_id,))
    existing = c.fetchone()
    
    if existing:
        # Student exists - Return their info
        conn.close()
        return {
            "status": "exists",
            "student_id": student_id,
            "name": existing[0],
            "email": existing[1],
            "message": f"Welcome back, {existing[0]}!"
        }
    else:
        # New student - Register
        c.execute('''
            INSERT INTO students (student_id, name, email, target_score)
            VALUES (?, ?, ?, 90)
        ''', (student_id, name, ""))
        
        conn.commit()
        conn.close()
        
        return {
            "status": "new",
            "student_id": student_id,
            "name": name,
            "email": "",
            "message": f"Welcome, {name}! Your profile is created."
        }


def get_chat_history(student_id: str, limit: int = 20):
    """Get chat history for student"""
    conn = sqlite3.connect(DATABASE_PATH)
    c = conn.cursor()
    
    c.execute('''
        SELECT message_type, content, timestamp 
        FROM chat_history 
        WHERE student_id = ? 
        ORDER BY timestamp DESC 
        LIMIT ?
    ''', (student_id, limit))
    
    messages = c.fetchall()
    conn.close()
    
    # Convert to list (reverse to show oldest first)
    history = []
    for msg_type, content, timestamp in reversed(messages):
        history.append({
            "role": msg_type,
            "content": content,
            "timestamp": timestamp
        })
    
    return history


def add_to_chat_history(student_id: str, message_type: str, content: str):
    """Add message to chat history"""
    conn = sqlite3.connect(DATABASE_PATH)
    c = conn.cursor()
    
    c.execute('''
        INSERT INTO chat_history (student_id, message_type, content)
        VALUES (?, ?, ?)
    ''', (student_id, message_type, content))
    
    conn.commit()
    conn.close()


def get_analytics(student_id: str):
    """Get analytics"""
    conn = sqlite3.connect(DATABASE_PATH)
    c = conn.cursor()
    
    # Total questions
    c.execute('SELECT COUNT(*) FROM student_progress WHERE student_id = ?', (student_id,))
    total_questions = c.fetchone()[0]
    
    # Accuracy
    c.execute('''
        SELECT AVG(CASE WHEN understood = 1 THEN 1 ELSE 0 END) * 100 
        FROM student_progress 
        WHERE student_id = ? AND understood IS NOT NULL
    ''', (student_id,))
    accuracy = c.fetchone()[0] or 0
    
    conn.close()
    
    return {
        'total_questions': total_questions,
        'accuracy': accuracy
    }


def track_question(student_id: str, chapter: str, subject: str, question: str, 
                   answer: str, time_spent: int, understood: bool = True, difficulty: str = "medium"):
    """Track question"""
    conn = sqlite3.connect(DATABASE_PATH)
    c = conn.cursor()
    
    c.execute('''
        INSERT INTO student_progress 
        (student_id, chapter, subject, question, answer, time_spent, understood, difficulty, date)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        student_id, chapter, subject, question, answer, 
        time_spent, understood, difficulty, datetime.now()
    ))
    
    conn.commit()
    conn.close()