from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class MovieProject(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    genre = db.Column(db.String(50), nullable=True)
    theme = db.Column(db.String(100), nullable=True)
    initial_idea = db.Column(db.Text, nullable=True)
    scenario_content = db.Column(db.Text, nullable=True)
    characters = db.Column(db.Text, nullable=True)  # JSON string
    scenes = db.Column(db.Text, nullable=True)  # JSON string
    status = db.Column(db.String(50), default='draft')  # draft, in_progress, completed, published
    output_path = db.Column(db.String(500), nullable=True)
    duration = db.Column(db.Float, nullable=True)  # المدة بالثواني
    resolution = db.Column(db.String(20), default='1920x1080')
    frame_rate = db.Column(db.Integer, default=24)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'genre': self.genre,
            'theme': self.theme,
            'initial_idea': self.initial_idea,
            'scenario_content': self.scenario_content,
            'characters': self.characters,
            'scenes': self.scenes,
            'status': self.status,
            'output_path': self.output_path,
            'duration': self.duration,
            'resolution': self.resolution,
            'frame_rate': self.frame_rate,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class Timeline(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    movie_id = db.Column(db.Integer, nullable=False)
    scene_id = db.Column(db.Integer, nullable=False)
    element_type = db.Column(db.String(50), nullable=False)  # video, image, audio, text
    element_id = db.Column(db.Integer, nullable=False)  # ID من الجدول المناسب
    start_time = db.Column(db.Float, nullable=False)  # وقت البداية بالثواني
    end_time = db.Column(db.Float, nullable=False)  # وقت النهاية بالثواني
    layer = db.Column(db.Integer, default=1)  # طبقة العنصر
    position_x = db.Column(db.Integer, default=0)  # الموضع الأفقي
    position_y = db.Column(db.Integer, default=0)  # الموضع العمودي
    scale = db.Column(db.Float, default=1.0)  # حجم العنصر
    opacity = db.Column(db.Float, default=1.0)  # الشفافية
    effects = db.Column(db.Text, nullable=True)  # JSON للمؤثرات
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'movie_id': self.movie_id,
            'scene_id': self.scene_id,
            'element_type': self.element_type,
            'element_id': self.element_id,
            'start_time': self.start_time,
            'end_time': self.end_time,
            'layer': self.layer,
            'position_x': self.position_x,
            'position_y': self.position_y,
            'scale': self.scale,
            'opacity': self.opacity,
            'effects': self.effects,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class RenderTask(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    movie_id = db.Column(db.Integer, nullable=False)
    task_type = db.Column(db.String(50), nullable=False)  # scene, full_movie, preview
    scene_id = db.Column(db.Integer, nullable=True)
    output_format = db.Column(db.String(20), default='mp4')
    quality = db.Column(db.String(20), default='high')  # low, medium, high, ultra
    status = db.Column(db.String(50), default='queued')  # queued, processing, completed, failed
    progress = db.Column(db.Integer, default=0)  # 0-100
    output_path = db.Column(db.String(500), nullable=True)
    error_message = db.Column(db.Text, nullable=True)
    render_settings = db.Column(db.Text, nullable=True)  # JSON string
    estimated_duration = db.Column(db.Integer, nullable=True)  # بالثواني
    actual_duration = db.Column(db.Integer, nullable=True)  # بالثواني
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'movie_id': self.movie_id,
            'task_type': self.task_type,
            'scene_id': self.scene_id,
            'output_format': self.output_format,
            'quality': self.quality,
            'status': self.status,
            'progress': self.progress,
            'output_path': self.output_path,
            'error_message': self.error_message,
            'render_settings': self.render_settings,
            'estimated_duration': self.estimated_duration,
            'actual_duration': self.actual_duration,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class AssetLibrary(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    movie_id = db.Column(db.Integer, nullable=False)
    asset_type = db.Column(db.String(50), nullable=False)  # image, video, audio, text
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    file_path = db.Column(db.String(500), nullable=False)
    file_size = db.Column(db.Integer, nullable=True)  # بالبايت
    duration = db.Column(db.Float, nullable=True)  # للفيديو والصوت
    dimensions = db.Column(db.String(20), nullable=True)  # للصور والفيديو
    metadata = db.Column(db.Text, nullable=True)  # JSON string
    tags = db.Column(db.String(500), nullable=True)  # مفصولة بفواصل
    is_generated = db.Column(db.Boolean, default=True)  # مولد أم مرفوع
    source_service = db.Column(db.String(100), nullable=True)  # scenario, visual, audio
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'movie_id': self.movie_id,
            'asset_type': self.asset_type,
            'name': self.name,
            'description': self.description,
            'file_path': self.file_path,
            'file_size': self.file_size,
            'duration': self.duration,
            'dimensions': self.dimensions,
            'metadata': self.metadata,
            'tags': self.tags,
            'is_generated': self.is_generated,
            'source_service': self.source_service,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

