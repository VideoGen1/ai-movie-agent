from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class Movie(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    genre = db.Column(db.String(100), nullable=True)
    theme = db.Column(db.Text, nullable=True)
    initial_idea = db.Column(db.Text, nullable=True)
    scenario = db.Column(db.Text, nullable=True)
    characters = db.Column(db.Text, nullable=True)  # JSON string
    scenes = db.Column(db.Text, nullable=True)  # JSON string
    status = db.Column(db.String(50), default='draft')  # draft, in_progress, completed
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'genre': self.genre,
            'theme': self.theme,
            'initial_idea': self.initial_idea,
            'scenario': self.scenario,
            'characters': self.characters,
            'scenes': self.scenes,
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class Scene(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    movie_id = db.Column(db.Integer, db.ForeignKey('movie.id'), nullable=False)
    scene_number = db.Column(db.Integer, nullable=False)
    title = db.Column(db.String(200), nullable=True)
    description = db.Column(db.Text, nullable=True)
    dialogue = db.Column(db.Text, nullable=True)
    visual_description = db.Column(db.Text, nullable=True)
    audio_description = db.Column(db.Text, nullable=True)
    duration = db.Column(db.Float, nullable=True)  # in seconds
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'movie_id': self.movie_id,
            'scene_number': self.scene_number,
            'title': self.title,
            'description': self.description,
            'dialogue': self.dialogue,
            'visual_description': self.visual_description,
            'audio_description': self.audio_description,
            'duration': self.duration,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class Character(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    movie_id = db.Column(db.Integer, db.ForeignKey('movie.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    personality = db.Column(db.Text, nullable=True)
    appearance = db.Column(db.Text, nullable=True)
    voice_description = db.Column(db.Text, nullable=True)
    role = db.Column(db.String(50), nullable=True)  # main, supporting, background
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'movie_id': self.movie_id,
            'name': self.name,
            'description': self.description,
            'personality': self.personality,
            'appearance': self.appearance,
            'voice_description': self.voice_description,
            'role': self.role,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

