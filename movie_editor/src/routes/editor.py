from flask import Blueprint, jsonify, request, send_file
from flask_cors import cross_origin
from src.models.movie_project import MovieProject, Timeline, RenderTask, AssetLibrary, db
from src.services.movie_editor import movie_editor
import json
import os
import uuid
from datetime import datetime
import threading
import logging
import requests

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

editor_bp = Blueprint('editor', __name__)

# مجلد حفظ الأفلام المولدة
GENERATED_MOVIES_DIR = os.path.join(os.path.dirname(__file__), '..', 'generated_movies')
os.makedirs(GENERATED_MOVIES_DIR, exist_ok=True)

# مجلد حفظ الأصول
ASSETS_DIR = os.path.join(os.path.dirname(__file__), '..', 'assets')
os.makedirs(ASSETS_DIR, exist_ok=True)

@editor_bp.route('/projects', methods=['GET'])
@cross_origin()
def get_projects():
    """الحصول على جميع مشاريع الأفلام"""
    projects = MovieProject.query.all()
    return jsonify([project.to_dict() for project in projects])

@editor_bp.route('/projects', methods=['POST'])
@cross_origin()
def create_project():
    """إنشاء مشروع فيلم جديد"""
    data = request.json
    
    project = MovieProject(
        title=data.get('title'),
        description=data.get('description'),
        genre=data.get('genre'),
        theme=data.get('theme'),
        initial_idea=data.get('initial_idea'),
        resolution=data.get('resolution', '1920x1080'),
        frame_rate=data.get('frame_rate', 24)
    )
    
    db.session.add(project)
    db.session.commit()
    
    return jsonify(project.to_dict()), 201

@editor_bp.route('/projects/<int:project_id>', methods=['GET'])
@cross_origin()
def get_project(project_id):
    """الحصول على مشروع فيلم محدد"""
    project = MovieProject.query.get_or_404(project_id)
    return jsonify(project.to_dict())

@editor_bp.route('/projects/<int:project_id>', methods=['PUT'])
@cross_origin()
def update_project(project_id):
    """تحديث مشروع فيلم"""
    project = MovieProject.query.get_or_404(project_id)
    data = request.json
    
    for key, value in data.items():
        if hasattr(project, key):
            setattr(project, key, value)
    
    project.updated_at = datetime.utcnow()
    db.session.commit()
    
    return jsonify(project.to_dict())

@editor_bp.route('/projects/<int:project_id>/timeline', methods=['GET'])
@cross_origin()
def get_timeline(project_id):
    """الحصول على الخط الزمني للمشروع"""
    timeline_items = Timeline.query.filter_by(movie_id=project_id).order_by(Timeline.start_time).all()
    return jsonify([item.to_dict() for item in timeline_items])

@editor_bp.route('/projects/<int:project_id>/timeline', methods=['POST'])
@cross_origin()
def add_timeline_item(project_id):
    """إضافة عنصر للخط الزمني"""
    data = request.json
    
    timeline_item = Timeline(
        movie_id=project_id,
        scene_id=data.get('scene_id'),
        element_type=data.get('element_type'),
        element_id=data.get('element_id'),
        start_time=data.get('start_time'),
        end_time=data.get('end_time'),
        layer=data.get('layer', 1),
        position_x=data.get('position_x', 0),
        position_y=data.get('position_y', 0),
        scale=data.get('scale', 1.0),
        opacity=data.get('opacity', 1.0),
        effects=json.dumps(data.get('effects', []))
    )
    
    db.session.add(timeline_item)
    db.session.commit()
    
    return jsonify(timeline_item.to_dict()), 201

@editor_bp.route('/timeline/<int:item_id>', methods=['PUT'])
@cross_origin()
def update_timeline_item(item_id):
    """تحديث عنصر في الخط الزمني"""
    item = Timeline.query.get_or_404(item_id)
    data = request.json
    
    for key, value in data.items():
        if hasattr(item, key):
            if key == 'effects':
                setattr(item, key, json.dumps(value))
            else:
                setattr(item, key, value)
    
    db.session.commit()
    return jsonify(item.to_dict())

@editor_bp.route('/timeline/<int:item_id>', methods=['DELETE'])
@cross_origin()
def delete_timeline_item(item_id):
    """حذف عنصر من الخط الزمني"""
    item = Timeline.query.get_or_404(item_id)
    db.session.delete(item)
    db.session.commit()
    
    return jsonify({'success': True})

@editor_bp.route('/projects/<int:project_id>/assets', methods=['GET'])
@cross_origin()
def get_project_assets(project_id):
    """الحصول على أصول المشروع"""
    asset_type = request.args.get('asset_type')
    
    query = AssetLibrary.query.filter_by(movie_id=project_id)
    
    if asset_type:
        query = query.filter_by(asset_type=asset_type)
    
    assets = query.all()
    return jsonify([asset.to_dict() for asset in assets])

@editor_bp.route('/projects/<int:project_id>/sync-assets', methods=['POST'])
@cross_origin()
def sync_project_assets(project_id):
    """مزامنة أصول المشروع من الخدمات الأخرى"""
    try:
        # مزامنة الصور من خدمة المحتوى البصري
        visual_assets = sync_visual_assets(project_id)
        
        # مزامنة الأصوات من خدمة المحتوى الصوتي
        audio_assets = sync_audio_assets(project_id)
        
        # مزامنة السيناريو من خدمة السيناريو
        scenario_assets = sync_scenario_assets(project_id)
        
        total_synced = len(visual_assets) + len(audio_assets) + len(scenario_assets)
        
        return jsonify({
            'success': True,
            'synced_assets': total_synced,
            'visual_assets': len(visual_assets),
            'audio_assets': len(audio_assets),
            'scenario_assets': len(scenario_assets)
        })
        
    except Exception as e:
        logger.error(f"Error syncing assets: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

def sync_visual_assets(project_id):
    """مزامنة الأصول البصرية"""
    try:
        # استدعاء خدمة المحتوى البصري
        response = requests.get(f'http://localhost:5001/api/visual-content?movie_id={project_id}')
        if response.status_code == 200:
            visual_content = response.json()
            
            synced_assets = []
            for item in visual_content:
                if item.get('status') == 'completed' and item.get('file_path'):
                    # التحقق من وجود الأصل في قاعدة البيانات
                    existing_asset = AssetLibrary.query.filter_by(
                        movie_id=project_id,
                        asset_type='image',
                        file_path=item['file_path']
                    ).first()
                    
                    if not existing_asset:
                        asset = AssetLibrary(
                            movie_id=project_id,
                            asset_type='image',
                            name=item.get('title', f"صورة مولدة {item['id']}"),
                            description=item.get('description'),
                            file_path=item['file_path'],
                            dimensions=f"{item.get('width', 512)}x{item.get('height', 512)}",
                            metadata=json.dumps(item),
                            tags=item.get('style', ''),
                            is_generated=True,
                            source_service='visual'
                        )
                        db.session.add(asset)
                        synced_assets.append(asset)
            
            db.session.commit()
            return synced_assets
            
    except Exception as e:
        logger.error(f"Error syncing visual assets: {str(e)}")
        return []

def sync_audio_assets(project_id):
    """مزامنة الأصول الصوتية"""
    try:
        # استدعاء خدمة المحتوى الصوتي
        response = requests.get(f'http://localhost:5002/api/audio-content?movie_id={project_id}')
        if response.status_code == 200:
            audio_content = response.json()
            
            synced_assets = []
            for item in audio_content:
                if item.get('status') == 'completed' and item.get('file_path'):
                    # التحقق من وجود الأصل في قاعدة البيانات
                    existing_asset = AssetLibrary.query.filter_by(
                        movie_id=project_id,
                        asset_type='audio',
                        file_path=item['file_path']
                    ).first()
                    
                    if not existing_asset:
                        asset = AssetLibrary(
                            movie_id=project_id,
                            asset_type='audio',
                            name=item.get('title', f"صوت مولد {item['id']}"),
                            description=item.get('description'),
                            file_path=item['file_path'],
                            duration=item.get('duration'),
                            metadata=json.dumps(item),
                            tags=item.get('content_type', ''),
                            is_generated=True,
                            source_service='audio'
                        )
                        db.session.add(asset)
                        synced_assets.append(asset)
            
            db.session.commit()
            return synced_assets
            
    except Exception as e:
        logger.error(f"Error syncing audio assets: {str(e)}")
        return []

def sync_scenario_assets(project_id):
    """مزامنة أصول السيناريو"""
    try:
        # استدعاء خدمة السيناريو
        response = requests.get(f'http://localhost:5000/api/movies/{project_id}')
        if response.status_code == 200:
            movie_data = response.json()
            
            synced_assets = []
            
            # إنشاء أصل للسيناريو
            if movie_data.get('scenario'):
                existing_asset = AssetLibrary.query.filter_by(
                    movie_id=project_id,
                    asset_type='text',
                    name='السيناريو الرئيسي'
                ).first()
                
                if not existing_asset:
                    asset = AssetLibrary(
                        movie_id=project_id,
                        asset_type='text',
                        name='السيناريو الرئيسي',
                        description='السيناريو المولد للفيلم',
                        file_path='',  # النص مخزن في metadata
                        metadata=json.dumps({
                            'content': movie_data['scenario'],
                            'type': 'scenario'
                        }),
                        tags='سيناريو,نص',
                        is_generated=True,
                        source_service='scenario'
                    )
                    db.session.add(asset)
                    synced_assets.append(asset)
            
            db.session.commit()
            return synced_assets
            
    except Exception as e:
        logger.error(f"Error syncing scenario assets: {str(e)}")
        return []

@editor_bp.route('/projects/<int:project_id>/render', methods=['POST'])
@cross_origin()
def render_movie(project_id):
    """تصدير الفيلم النهائي"""
    try:
        data = request.json
        output_format = data.get('output_format', 'mp4')
        quality = data.get('quality', 'high')
        scene_id = data.get('scene_id')  # إذا كان المطلوب تصدير مشهد واحد فقط
        
        # إنشاء مهمة تصدير
        render_task = RenderTask(
            movie_id=project_id,
            task_type='scene' if scene_id else 'full_movie',
            scene_id=scene_id,
            output_format=output_format,
            quality=quality,
            render_settings=json.dumps(data),
            status='processing'
        )
        db.session.add(render_task)
        db.session.commit()
        
        # بدء التصدير في خيط منفصل
        thread = threading.Thread(
            target=render_movie_async,
            args=(render_task.id, project_id, scene_id, output_format, quality)
        )
        thread.start()
        
        return jsonify({
            'success': True,
            'task_id': render_task.id,
            'message': 'بدأ تصدير الفيلم'
        })
        
    except Exception as e:
        logger.error(f"Error starting movie render: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

def render_movie_async(task_id, project_id, scene_id, output_format, quality):
    """تصدير الفيلم بشكل غير متزامن"""
    try:
        task = RenderTask.query.get(task_id)
        if not task:
            return
        
        task.progress = 10
        db.session.commit()
        
        # الحصول على بيانات الخط الزمني
        query = Timeline.query.filter_by(movie_id=project_id)
        if scene_id:
            query = query.filter_by(scene_id=scene_id)
        
        timeline_items = query.order_by(Timeline.start_time).all()
        timeline_data = [item.to_dict() for item in timeline_items]
        
        if not timeline_data:
            task.status = 'failed'
            task.error_message = 'لا توجد عناصر في الخط الزمني'
            db.session.commit()
            return
        
        task.progress = 30
        db.session.commit()
        
        # إنشاء اسم الملف
        project = MovieProject.query.get(project_id)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"{project.title}_{timestamp}.{output_format}"
        output_path = os.path.join(GENERATED_MOVIES_DIR, filename)
        
        # إعدادات التصدير
        settings = {
            'resolution': tuple(map(int, project.resolution.split('x'))),
            'fps': project.frame_rate,
            'quality': quality
        }
        
        task.progress = 50
        db.session.commit()
        
        # تصدير الفيلم
        success = movie_editor.create_movie_from_timeline(
            timeline_data, 
            output_path, 
            settings
        )
        
        if success:
            # الحصول على معلومات الفيديو
            movie_info = movie_editor.get_movie_info(output_path)
            
            # تحديث المشروع
            project.output_path = output_path
            if movie_info:
                project.duration = movie_info.get('duration')
            
            # تحديث المهمة
            task.status = 'completed'
            task.output_path = output_path
            task.progress = 100
            
            db.session.commit()
            
            logger.info(f"Movie render completed for project {project_id}")
        else:
            task.status = 'failed'
            task.error_message = 'فشل في تصدير الفيلم'
            db.session.commit()
            
    except Exception as e:
        logger.error(f"Error in render_movie_async: {str(e)}")
        task = RenderTask.query.get(task_id)
        if task:
            task.status = 'failed'
            task.error_message = str(e)
            db.session.commit()

@editor_bp.route('/projects/<int:project_id>/preview', methods=['POST'])
@cross_origin()
def create_preview(project_id):
    """إنشاء معاينة سريعة للفيلم"""
    try:
        data = request.json
        duration = data.get('duration', 10)  # مدة المعاينة بالثواني
        
        # الحصول على بيانات الخط الزمني
        timeline_items = Timeline.query.filter_by(movie_id=project_id).order_by(Timeline.start_time).all()
        timeline_data = [item.to_dict() for item in timeline_items]
        
        if not timeline_data:
            return jsonify({'success': False, 'error': 'لا توجد عناصر في الخط الزمني'}), 400
        
        # إنشاء المعاينة
        preview_path = movie_editor.create_preview(timeline_data, duration)
        
        if preview_path:
            return jsonify({
                'success': True,
                'preview_path': preview_path,
                'message': 'تم إنشاء المعاينة بنجاح'
            })
        else:
            return jsonify({'success': False, 'error': 'فشل في إنشاء المعاينة'}), 500
            
    except Exception as e:
        logger.error(f"Error creating preview: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@editor_bp.route('/render-tasks', methods=['GET'])
@cross_origin()
def get_render_tasks():
    """الحصول على مهام التصدير"""
    movie_id = request.args.get('movie_id')
    
    query = RenderTask.query
    if movie_id:
        query = query.filter_by(movie_id=movie_id)
    
    tasks = query.order_by(RenderTask.created_at.desc()).all()
    return jsonify([task.to_dict() for task in tasks])

@editor_bp.route('/render-tasks/<int:task_id>', methods=['GET'])
@cross_origin()
def get_render_task_status(task_id):
    """الحصول على حالة مهمة التصدير"""
    task = RenderTask.query.get_or_404(task_id)
    return jsonify(task.to_dict())

@editor_bp.route('/files/<path:filename>')
@cross_origin()
def serve_movie_file(filename):
    """تقديم ملفات الأفلام المولدة"""
    try:
        file_path = os.path.join(GENERATED_MOVIES_DIR, filename)
        if os.path.exists(file_path):
            return send_file(file_path)
        else:
            return jsonify({'error': 'File not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@editor_bp.route('/projects/<int:project_id>/auto-timeline', methods=['POST'])
@cross_origin()
def create_auto_timeline(project_id):
    """إنشاء خط زمني تلقائي من الأصول المتاحة"""
    try:
        # مزامنة الأصول أولاً
        sync_project_assets(project_id)
        
        # الحصول على الأصول
        assets = AssetLibrary.query.filter_by(movie_id=project_id).all()
        
        if not assets:
            return jsonify({'success': False, 'error': 'لا توجد أصول متاحة'}), 400
        
        # تجميع الأصول حسب النوع
        images = [a for a in assets if a.asset_type == 'image']
        audios = [a for a in assets if a.asset_type == 'audio']
        texts = [a for a in assets if a.asset_type == 'text']
        
        # إنشاء خط زمني تلقائي
        current_time = 0
        scene_duration = 5  # مدة كل مشهد بالثواني
        
        # حذف الخط الزمني الموجود
        Timeline.query.filter_by(movie_id=project_id).delete()
        
        # إضافة الصور
        for i, image in enumerate(images):
            timeline_item = Timeline(
                movie_id=project_id,
                scene_id=i + 1,
                element_type='image',
                element_id=image.id,
                start_time=current_time,
                end_time=current_time + scene_duration,
                layer=1
            )
            db.session.add(timeline_item)
            current_time += scene_duration
        
        # إضافة الأصوات
        if audios:
            audio_start = 0
            for audio in audios:
                duration = audio.duration or 10
                timeline_item = Timeline(
                    movie_id=project_id,
                    scene_id=1,
                    element_type='audio',
                    element_id=audio.id,
                    start_time=audio_start,
                    end_time=audio_start + duration,
                    layer=2
                )
                db.session.add(timeline_item)
                audio_start += duration
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'تم إنشاء الخط الزمني التلقائي',
            'total_duration': current_time
        })
        
    except Exception as e:
        logger.error(f"Error creating auto timeline: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

