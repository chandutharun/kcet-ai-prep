"""
Personal AI for each student - Performance tracking & adaptive learning
"""

import sqlite3
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional
from src.config import DATABASE_PATH


class PersonalAI:
    """Personal AI assistant for each student"""
    
    def __init__(self, student_id: str = "default"):
        self.student_id = student_id
        self.init_db()
    
    def init_db(self):
        """Initialize database for personal AI"""
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        
        # Student profile
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS students (
                student_id TEXT PRIMARY KEY,
                name TEXT,
                email TEXT,
                created_at DATETIME,
                target_score INTEGER,
                strong_subjects TEXT,
                weak_subjects TEXT
            )
        ''')
        
        # Performance tracking
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS performance (
                id INTEGER PRIMARY KEY,
                student_id TEXT,
                subject TEXT,
                topic TEXT,
                question_type TEXT,
                accuracy REAL,
                time_taken REAL,
                timestamp DATETIME
            )
        ''')
        
        # Learning history
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS learning_history (
                id INTEGER PRIMARY KEY,
                student_id TEXT,
                question TEXT,
                answer TEXT,
                subject TEXT,
                difficulty TEXT,
                understood BOOLEAN,
                timestamp DATETIME
            )
        ''')
        
        # Quiz results
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS quiz_results (
                id INTEGER PRIMARY KEY,
                student_id TEXT,
                quiz_name TEXT,
                subject TEXT,
                total_questions INTEGER,
                correct_answers INTEGER,
                score REAL,
                timestamp DATETIME
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def register_student(self, name: str, email: str, target_score: int = 90):
        """Register new student"""
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT OR REPLACE INTO students 
            (student_id, name, email, created_at, target_score)
            VALUES (?, ?, ?, ?, ?)
        ''', (self.student_id, name, email, datetime.now(), target_score))
        
        conn.commit()
        conn.close()
        
        return {"status": "success", "student_id": self.student_id}
    
    def track_question(self, question: str, answer: str, subject: str, 
                       difficulty: str, understood: bool, time_taken: float = 0):
        """Track question-answer interaction"""
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        
        # Learning history
        cursor.execute('''
            INSERT INTO learning_history 
            (student_id, question, answer, subject, difficulty, understood, timestamp)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (self.student_id, question, answer, subject, difficulty, understood, datetime.now()))
        
        # Performance tracking
        cursor.execute('''
            INSERT INTO performance 
            (student_id, subject, topic, question_type, accuracy, time_taken, timestamp)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            self.student_id, 
            subject, 
            self._extract_topic(question), 
            'conceptual',
            1.0 if understood else 0.0,
            time_taken,
            datetime.now()
        ))
        
        conn.commit()
        conn.close()
    
    def track_quiz(self, quiz_name: str, subject: str, total: int, correct: int):
        """Track quiz results"""
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        
        score = (correct / total) * 100 if total > 0 else 0
        
        cursor.execute('''
            INSERT INTO quiz_results 
            (student_id, quiz_name, subject, total_questions, correct_answers, score, timestamp)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (self.student_id, quiz_name, subject, total, correct, score, datetime.now()))
        
        conn.commit()
        conn.close()
        
        return {"score": score, "correct": correct, "total": total}
    
    def get_performance_stats(self) -> Dict:
        """Get student performance statistics"""
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        
        # Overall accuracy
        cursor.execute('''
            SELECT AVG(accuracy) FROM performance 
            WHERE student_id = ?
        ''', (self.student_id,))
        overall_accuracy = cursor.fetchone()[0] or 0
        
        # By subject
        cursor.execute('''
            SELECT subject, AVG(accuracy), COUNT(*) 
            FROM performance 
            WHERE student_id = ?
            GROUP BY subject
        ''', (self.student_id,))
        subject_stats = cursor.fetchall()
        
        # Recent activity
        cursor.execute('''
            SELECT question, subject, understood, timestamp 
            FROM learning_history 
            WHERE student_id = ?
            ORDER BY timestamp DESC 
            LIMIT 10
        ''', (self.student_id,))
        recent = cursor.fetchall()
        
        # Weak subjects (lowest accuracy)
        cursor.execute('''
            SELECT subject, AVG(accuracy) 
            FROM performance 
            WHERE student_id = ?
            GROUP BY subject
            ORDER BY AVG(accuracy) ASC
            LIMIT 3
        ''', (self.student_id,))
        weak_subjects = cursor.fetchall()
        
        # Strong subjects
        cursor.execute('''
            SELECT subject, AVG(accuracy) 
            FROM performance 
            WHERE student_id = ?
            GROUP BY subject
            ORDER BY AVG(accuracy) DESC
            LIMIT 3
        ''', (self.student_id,))
        strong_subjects = cursor.fetchall()
        
        conn.close()
        
        return {
            'overall_accuracy': overall_accuracy * 100,
            'subject_stats': subject_stats,
            'recent_activity': recent,
            'weak_subjects': weak_subjects,
            'strong_subjects': strong_subjects,
            'total_questions': len(recent)
        }
    
    def get_adaptive_recommendations(self) -> List[str]:
        """Get personalized learning recommendations based on performance"""
        stats = self.get_performance_stats()
        recommendations = []
        
        # Weak subjects priority
        for subject, accuracy in stats['weak_subjects']:
            if accuracy < 50:
                recommendations.append(
                    f"🔴 Focus on {subject}: Your accuracy is {accuracy*100:.1f}% - need more practice"
                )
        
        # Strong subjects maintenance
        for subject, accuracy in stats['strong_subjects']:
            if accuracy > 70:
                recommendations.append(
                    f"🟢 Good in {subject}: {accuracy*100:.1f}% - keep practicing to maintain"
                )
        
        # Overall progress
        if stats['overall_accuracy'] < 60:
            recommendations.append(
                "⚠️ Overall accuracy is low ({:.1f}%). Focus on basics first".format(
                    stats['overall_accuracy']
                )
            )
        elif stats['overall_accuracy'] > 80:
            recommendations.append(
                "✅ Great progress! ({:.1f}%). Try advanced problems".format(
                    stats['overall_accuracy']
                )
            )
        
        # Study plan
        if len(stats['recent_activity']) < 10:
            recommendations.append("📚 Start daily practice: Ask at least 10 questions today")
        else:
            recommendations.append("📚 Keep the momentum! You're on track")
        
        return recommendations
    
    def _extract_topic(self, question: str) -> str:
        """Extract topic from question (simple keyword matching)"""
        keywords = {
            "motion": "Mechanics",
            "force": "Mechanics",
            "energy": "Energy & Work",
            "power": "Energy & Work",
            "electricity": "Electricity",
            "magnetism": " Magnetism",
            "optics": "Optics",
            "thermo": "Thermodynamics",
            "chemistry": "General Chemistry",
            "organic": "Organic Chemistry",
            "integration": "Calculus",
            "derivative": "Calculus",
            "algebra": "Algebra",
            "geometry": "Geometry",
            "trigonometry": "Trigonometry",
            "cell": "Cell Biology",
            "dna": "Genetics",
            "evolution": "Evolution"
        }
        
        question_lower = question.lower()
        for keyword, topic in keywords.items():
            if keyword in question_lower:
                return topic
        
        return "General"
    
    def generate_study_plan(self, days: int = 7) -> Dict:
        """Generate personalized study plan"""
        stats = self.get_performance_stats()
        
        plan = {
            'days': days,
            'focus_subjects': [],
            'daily_goals': [],
            'recommendations': []
        }
        
        # Focus on weak subjects
        for subject, accuracy in stats['weak_subjects'][:2]:
            plan['focus_subjects'].append({
                'subject': subject,
                'current_accuracy': accuracy * 100,
                'target_accuracy': 70,
                'priority': 'high'
            })
        
        # Daily goals
        for day in range(1, days + 1):
            plan['daily_goals'].append({
                'day': day,
                'questions_to_ask': 10,
                'quizzes_to_take': 1,
                'focus_subject': plan['focus_subjects'][0]['subject'] if plan['focus_subjects'] else 'Physics'
            })
        
        plan['recommendations'] = self.get_adaptive_recommendations()
        
        return plan
    
    def get_progress_chart_data(self) -> Dict:
        """Get data for progress chart"""
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        
        # Last 7 days activity
        cursor.execute('''
            SELECT DATE(timestamp) as date, COUNT(*), AVG(accuracy)
            FROM learning_history 
            WHERE student_id = ?
            AND timestamp >= DATE('now', '-7 days')
            GROUP BY DATE(timestamp)
            ORDER BY date
        ''', (self.student_id,))
        
        daily_progress = cursor.fetchall()
        conn.close()
        
        return {
            'dates': [row[0] for row in daily_progress],
            'question_count': [row[1] for row in daily_progress],
            'accuracy': [row[2] * 100 if row[2] else 0 for row in daily_progress]
        }
