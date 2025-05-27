import os
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase

class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)

class ChatSession(db.Model):
    """Store chat sessions for analytics and user experience"""
    __tablename__ = 'chat_sessions'
    
    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.String(100), unique=True, nullable=False)
    user_ip = db.Column(db.String(50))
    user_agent = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_activity = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationship with messages
    messages = db.relationship('ChatMessage', backref='session', lazy=True, cascade='all, delete-orphan')

class ChatMessage(db.Model):
    """Store individual chat messages"""
    __tablename__ = 'chat_messages'
    
    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.String(100), db.ForeignKey('chat_sessions.session_id'), nullable=False)
    message_type = db.Column(db.String(20), nullable=False)  # 'user' or 'bot'
    content = db.Column(db.Text, nullable=False)
    source = db.Column(db.String(50))  # 'faq', 'ai-assistant', 'fallback', etc.
    confidence_score = db.Column(db.Float)
    response_time = db.Column(db.Float)  # Time taken to generate response
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

class FAQAnalytics(db.Model):
    """Track FAQ usage and popular questions"""
    __tablename__ = 'faq_analytics'
    
    id = db.Column(db.Integer, primary_key=True)
    question_hash = db.Column(db.String(64), unique=True, nullable=False)  # Hash of the question
    original_question = db.Column(db.Text, nullable=False)
    category = db.Column(db.String(50))
    hit_count = db.Column(db.Integer, default=1)
    avg_confidence = db.Column(db.Float)
    last_accessed = db.Column(db.DateTime, default=datetime.utcnow)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class UserFeedback(db.Model):
    """Store user feedback on chatbot responses"""
    __tablename__ = 'user_feedback'
    
    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.String(100), db.ForeignKey('chat_sessions.session_id'))
    message_id = db.Column(db.Integer, db.ForeignKey('chat_messages.id'))
    rating = db.Column(db.Integer)  # 1-5 star rating
    feedback_text = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)