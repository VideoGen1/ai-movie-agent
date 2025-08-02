from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class AudioContent(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    movie_id = db.Column(db.Integer, nullable=False)
    scene_id = db.Column(db.Integer, nullable=True)
    content_type = db.Column(db.String(50), nullable=False)  # voice, music, sound_effect, narration
    title = db.Column(db.String(200), nullable=True)
    description = db.Column(db.Text, nullable=True)
    text_content = db.Column(db.Text, nullable=True)  # للنصوص المراد تحويلها لصوت
    file_path = db.Column(db.String(500), nullable=True)
    file_url = db.Column(db.String(500), nullable=True)
    duration = db.Column(db.Float, nullable=True)  # المدة بالثواني
    sample_rate = db.Column(db.Integer, nullable=True)  # معدل العينة
    channels = db.Column(db.Integer, nullable=True)  # عدد القنوات (mono/stereo)
    voice_type = db.Column(db.String(50), nullable=True)  # male, female, child, etc.
    language = db.Column(db.String(10), default='ar')  # اللغة
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
            'text_content': self.text_content,
            'file_path': self.file_path,
            'file_url': self.file_url,
            'duration': self.duration,
            'sample_rate': self.sample_rate,
            'channels': self.channels,
            'voice_type': self.voice_type,
            'language': self.language,
            'model_used': self.model_used,
            'generation_params': self.generation_params,
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class AudioTask(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    task_type = db.Column(db.String(50), nullable=False)  # tts, music, sound_effect, voice_clone
    movie_id = db.Column(db.Integer, nullable=False)
    scene_id = db.Column(db.Integer, nullable=True)
    text_content = db.Column(db.Text, nullable=True)
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
            'text_content': self.text_content,
            'parameters': self.parameters,
            'status': self.status,
            'result_path': self.result_path,
            'error_message': self.error_message,
            'progress': self.progress,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class VoiceProfile(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    voice_type = db.Column(db.String(50), nullable=False)  # male, female, child
    language = db.Column(db.String(10), default='ar')
    sample_file_path = db.Column(db.String(500), nullable=True)
    is_default = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'voice_type': self.voice_type,
            'language': self.language,
            'sample_file_path': self.sample_file_path,
            'is_default': self.is_default,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

