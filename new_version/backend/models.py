from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, Float, Boolean, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    email = Column(String(120), unique=True)
    face_id = Column(String(100), unique=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    conversations = relationship('Conversation', back_populates='user')
    reminders = relationship('Reminder', back_populates='user')

class Conversation(Base):
    __tablename__ = 'conversations'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    title = Column(String(200))
    audio_path = Column(String(500))
    transcript = Column(Text)
    summary = Column(Text)
    duration = Column(Float)
    word_count = Column(Integer)
    speaker_count = Column(Integer, default=1)
    location = Column(String(200))
    timestamp = Column(DateTime, default=datetime.utcnow)
    is_audio_deleted = Column(Boolean, default=False)
    
    user = relationship('User', back_populates='conversations')
    speakers = relationship('Speaker', back_populates='conversation', cascade='all, delete-orphan')
    keynotes = relationship('Keynote', back_populates='conversation', cascade='all, delete-orphan')

class Speaker(Base):
    __tablename__ = 'speakers'
    
    id = Column(Integer, primary_key=True)
    conversation_id = Column(Integer, ForeignKey('conversations.id'))
    speaker_label = Column(String(50))
    speaker_name = Column(String(100))
    total_duration = Column(Float)
    
    conversation = relationship('Conversation', back_populates='speakers')
    segments = relationship('SpeakerSegment', back_populates='speaker', cascade='all, delete-orphan')

class SpeakerSegment(Base):
    __tablename__ = 'speaker_segments'
    
    id = Column(Integer, primary_key=True)
    speaker_id = Column(Integer, ForeignKey('speakers.id'))
    start_time = Column(Float)
    end_time = Column(Float)
    text = Column(Text)
    confidence = Column(Float)
    
    speaker = relationship('Speaker', back_populates='segments')

class Keynote(Base):
    __tablename__ = 'keynotes'
    
    id = Column(Integer, primary_key=True)
    conversation_id = Column(Integer, ForeignKey('conversations.id'))
    content = Column(Text, nullable=False)
    importance_score = Column(Float)
    category = Column(String(50))
    timestamp = Column(DateTime, default=datetime.utcnow)
    is_completed = Column(Boolean, default=False)
    
    conversation = relationship('Conversation', back_populates='keynotes')
    reminder = relationship('Reminder', back_populates='keynote', uselist=False)

class Reminder(Base):
    __tablename__ = 'reminders'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    keynote_id = Column(Integer, ForeignKey('keynotes.id'))
    reminder_time = Column(DateTime, nullable=False)
    is_sent = Column(Boolean, default=False)
    sent_at = Column(DateTime)
    
    user = relationship('User', back_populates='reminders')
    keynote = relationship('Keynote', back_populates='reminder')

# Database setup
engine = create_engine('sqlite:///ai_pendant.db', echo=False)
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)

def get_db():
    return Session()