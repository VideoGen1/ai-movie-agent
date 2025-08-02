from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class VisualContent(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    movie_id = db.Column(db.Integer, nullable=False)
    scene_id = db.Column(db.Integer, nullable=True)
    content_type = db.Column(db.String(50), nullable=False)  # image, video, effect
    title = db.Column(db.String(200), nullable=True)
    description = db.Column(db.Text, nullable=True)
    prompt = db.Column(db.Text, nullable=True)
    file_path = db.Column(db.String(500), nullable=True)
    file_url = db.Column(db.String(500), nullable=True)
    width = db.Column(db.Integer, nullable=True)
    height = db.Column(db.Integer, nullable=True)
    duration = db.Column(db.Float, nullable=True)  # for videos in seconds
    model_used = db.Column(db.String(100), nullable=True)
    generation_params = db.Column(db.Text, nullable=True)  # JSON string
    status = db.Column(db.String(50), default='pending')  # pending, generating, completed, failed
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'movie_id': self.movie_id,
            'scene_id': self.scene_id,
            'content_type': self.content_type,
            'title': self.title,
            'description': self.description,
            'prompt': self.prompt,
            'file_path': self.file_path,
            'file_url': self.file_url,
            'width': self.width,
            'height': self.height,
            'duration': self.duration,
            'model_used': self.model_used,
            'generation_params': self.generation_params,
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class GenerationTask(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    task_type = db.Column(db.String(50), nullable=False)  # image, video, effect
    movie_id = db.Column(db.Integer, nullable=False)
    scene_id = db.Column(db.Integer, nullable=True)
    prompt = db.Column(db.Text, nullable=False)
    parameters = db.Column(db.Text, nullable=True)  # JSON string
    status = db.Column(db.String(50), default='queued')  # queued, processing, completed, failed
    result_path = db.Column(db.String(500), nullable=True)
    error_message = db.Column(db.Text, nullable=True)
    progress = db.Column(db.Integer, default=0)  # 0-100
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'task_type': self.task_type,
            'movie_id': self.movie_id,
            'scene_id': self.scene_id,
            'prompt': self.prompt,
            'parameters': self.parameters,
            'status': self.status,
            'result_path': self.result_path,
            'error_message': self.error_message,
            'progress': self.progress,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

