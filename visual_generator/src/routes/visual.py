from flask import Blueprint, jsonify, request, send_file
from flask_cors import cross_origin
from src.models.visual_content import VisualContent, GenerationTask, db
from src.services.image_generator import image_generator
import json
import os
import uuid
from datetime import datetime
import threading
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

visual_bp = Blueprint('visual', __name__)

# مجلد حفظ الملفات المولدة
GENERATED_FILES_DIR = os.path.join(os.path.dirname(__file__), '..', 'generated_files')
os.makedirs(GENERATED_FILES_DIR, exist_ok=True)

@visual_bp.route('/visual-content', methods=['GET'])
@cross_origin()
def get_visual_content():
    """الحصول على جميع المحتوى البصري"""
    movie_id = request.args.get('movie_id')
    scene_id = request.args.get('scene_id')
    content_type = request.args.get('content_type')
    
    query = VisualContent.query
    
    if movie_id:
        query = query.filter_by(movie_id=movie_id)
    if scene_id:
        query = query.filter_by(scene_id=scene_id)
    if content_type:
        query = query.filter_by(content_type=content_type)
    
    content = query.all()
    return jsonify([item.to_dict() for item in content])

@visual_bp.route('/visual-content', methods=['POST'])
@cross_origin()
def create_visual_content():
    """إنشاء محتوى بصري جديد"""
    data = request.json
    
    content = VisualContent(
        movie_id=data.get('movie_id'),
        scene_id=data.get('scene_id'),
        content_type=data.get('content_type', 'image'),
        title=data.get('title'),
        description=data.get('description'),
        prompt=data.get('prompt')
    )
    
    db.session.add(content)
    db.session.commit()
    
    return jsonify(content.to_dict()), 201

@visual_bp.route('/generate-image', methods=['POST'])
@cross_origin()
def generate_image():
    """توليد صورة من النص"""
    try:
        data = request.json
        prompt = data.get('prompt', '')
        movie_id = data.get('movie_id')
        scene_id = data.get('scene_id')
        
        if not prompt:
            return jsonify({'success': False, 'error': 'Prompt is required'}), 400
        
        # إنشاء مهمة توليد
        task = GenerationTask(
            task_type='image',
            movie_id=movie_id,
            scene_id=scene_id,
            prompt=prompt,
            parameters=json.dumps(data.get('parameters', {})),
            status='processing'
        )
        db.session.add(task)
        db.session.commit()
        
        # بدء توليد الصورة في خيط منفصل
        thread = threading.Thread(
            target=generate_image_async,
            args=(task.id, prompt, data.get('parameters', {}))
        )
        thread.start()
        
        return jsonify({
            'success': True,
            'task_id': task.id,
            'message': 'Image generation started'
        })
        
    except Exception as e:
        logger.error(f"Error in generate_image: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

def generate_image_async(task_id, prompt, parameters):
    """توليد الصورة بشكل غير متزامن"""
    try:
        # الحصول على المهمة
        task = GenerationTask.query.get(task_id)
        if not task:
            return
        
        # تحديث حالة المهمة
        task.status = 'processing'
        task.progress = 10
        db.session.commit()
        
        # تحميل النموذج
        if not image_generator.load_model():
            task.status = 'failed'
            task.error_message = 'Failed to load image generation model'
            db.session.commit()
            return
        
        task.progress = 30
        db.session.commit()
        
        # توليد الصورة
        image = image_generator.generate_image(
            prompt=prompt,
            width=parameters.get('width', 512),
            height=parameters.get('height', 512),
            num_inference_steps=parameters.get('steps', 20),
            guidance_scale=parameters.get('guidance_scale', 7.5),
            seed=parameters.get('seed')
        )
        
        task.progress = 80
        db.session.commit()
        
        # حفظ الصورة
        filename = f"image_{task_id}_{uuid.uuid4().hex[:8]}.png"
        file_path = os.path.join(GENERATED_FILES_DIR, filename)
        
        if image_generator.save_image(image, file_path):
            # إنشاء سجل المحتوى البصري
            visual_content = VisualContent(
                movie_id=task.movie_id,
                scene_id=task.scene_id,
                content_type='image',
                title=f"Generated Image - {task_id}",
                prompt=prompt,
                file_path=file_path,
                width=image.width,
                height=image.height,
                model_used='stable-diffusion-v1-5',
                generation_params=task.parameters,
                status='completed'
            )
            db.session.add(visual_content)
            
            # تحديث المهمة
            task.status = 'completed'
            task.result_path = file_path
            task.progress = 100
            db.session.commit()
            
            logger.info(f"Image generation completed for task {task_id}")
        else:
            task.status = 'failed'
            task.error_message = 'Failed to save generated image'
            db.session.commit()
            
    except Exception as e:
        logger.error(f"Error in generate_image_async: {str(e)}")
        task = GenerationTask.query.get(task_id)
        if task:
            task.status = 'failed'
            task.error_message = str(e)
            db.session.commit()

@visual_bp.route('/generate-character-image', methods=['POST'])
@cross_origin()
def generate_character_image():
    """توليد صورة شخصية"""
    try:
        data = request.json
        character_description = data.get('character_description', '')
        style = data.get('style', 'realistic')
        movie_id = data.get('movie_id')
        
        if not character_description:
            return jsonify({'success': False, 'error': 'Character description is required'}), 400
        
        # إنشاء مهمة توليد
        task = GenerationTask(
            task_type='character_image',
            movie_id=movie_id,
            prompt=character_description,
            parameters=json.dumps({'style': style}),
            status='processing'
        )
        db.session.add(task)
        db.session.commit()
        
        # بدء توليد الصورة في خيط منفصل
        thread = threading.Thread(
            target=generate_character_image_async,
            args=(task.id, character_description, style)
        )
        thread.start()
        
        return jsonify({
            'success': True,
            'task_id': task.id,
            'message': 'Character image generation started'
        })
        
    except Exception as e:
        logger.error(f"Error in generate_character_image: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

def generate_character_image_async(task_id, character_description, style):
    """توليد صورة الشخصية بشكل غير متزامن"""
    try:
        task = GenerationTask.query.get(task_id)
        if not task:
            return
        
        task.progress = 20
        db.session.commit()
        
        # تحميل النموذج
        if not image_generator.load_model():
            task.status = 'failed'
            task.error_message = 'Failed to load image generation model'
            db.session.commit()
            return
        
        task.progress = 50
        db.session.commit()
        
        # توليد صورة الشخصية
        image = image_generator.generate_character_image(character_description, style)
        
        task.progress = 90
        db.session.commit()
        
        # حفظ الصورة
        filename = f"character_{task_id}_{uuid.uuid4().hex[:8]}.png"
        file_path = os.path.join(GENERATED_FILES_DIR, filename)
        
        if image_generator.save_image(image, file_path):
            # إنشاء سجل المحتوى البصري
            visual_content = VisualContent(
                movie_id=task.movie_id,
                content_type='character_image',
                title=f"Character Image - {task_id}",
                description=character_description,
                prompt=character_description,
                file_path=file_path,
                width=image.width,
                height=image.height,
                model_used='stable-diffusion-v1-5',
                generation_params=task.parameters,
                status='completed'
            )
            db.session.add(visual_content)
            
            task.status = 'completed'
            task.result_path = file_path
            task.progress = 100
            db.session.commit()
            
        else:
            task.status = 'failed'
            task.error_message = 'Failed to save generated character image'
            db.session.commit()
            
    except Exception as e:
        logger.error(f"Error in generate_character_image_async: {str(e)}")
        task = GenerationTask.query.get(task_id)
        if task:
            task.status = 'failed'
            task.error_message = str(e)
            db.session.commit()

@visual_bp.route('/generate-scene-image', methods=['POST'])
@cross_origin()
def generate_scene_image():
    """توليد صورة مشهد"""
    try:
        data = request.json
        scene_description = data.get('scene_description', '')
        mood = data.get('mood', 'neutral')
        movie_id = data.get('movie_id')
        scene_id = data.get('scene_id')
        
        if not scene_description:
            return jsonify({'success': False, 'error': 'Scene description is required'}), 400
        
        # إنشاء مهمة توليد
        task = GenerationTask(
            task_type='scene_image',
            movie_id=movie_id,
            scene_id=scene_id,
            prompt=scene_description,
            parameters=json.dumps({'mood': mood}),
            status='processing'
        )
        db.session.add(task)
        db.session.commit()
        
        # بدء توليد الصورة في خيط منفصل
        thread = threading.Thread(
            target=generate_scene_image_async,
            args=(task.id, scene_description, mood)
        )
        thread.start()
        
        return jsonify({
            'success': True,
            'task_id': task.id,
            'message': 'Scene image generation started'
        })
        
    except Exception as e:
        logger.error(f"Error in generate_scene_image: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

def generate_scene_image_async(task_id, scene_description, mood):
    """توليد صورة المشهد بشكل غير متزامن"""
    try:
        task = GenerationTask.query.get(task_id)
        if not task:
            return
        
        task.progress = 20
        db.session.commit()
        
        # تحميل النموذج
        if not image_generator.load_model():
            task.status = 'failed'
            task.error_message = 'Failed to load image generation model'
            db.session.commit()
            return
        
        task.progress = 50
        db.session.commit()
        
        # توليد صورة المشهد
        image = image_generator.generate_scene_image(scene_description, mood)
        
        task.progress = 90
        db.session.commit()
        
        # حفظ الصورة
        filename = f"scene_{task_id}_{uuid.uuid4().hex[:8]}.png"
        file_path = os.path.join(GENERATED_FILES_DIR, filename)
        
        if image_generator.save_image(image, file_path):
            # إنشاء سجل المحتوى البصري
            visual_content = VisualContent(
                movie_id=task.movie_id,
                scene_id=task.scene_id,
                content_type='scene_image',
                title=f"Scene Image - {task_id}",
                description=scene_description,
                prompt=scene_description,
                file_path=file_path,
                width=image.width,
                height=image.height,
                model_used='stable-diffusion-v1-5',
                generation_params=task.parameters,
                status='completed'
            )
            db.session.add(visual_content)
            
            task.status = 'completed'
            task.result_path = file_path
            task.progress = 100
            db.session.commit()
            
        else:
            task.status = 'failed'
            task.error_message = 'Failed to save generated scene image'
            db.session.commit()
            
    except Exception as e:
        logger.error(f"Error in generate_scene_image_async: {str(e)}")
        task = GenerationTask.query.get(task_id)
        if task:
            task.status = 'failed'
            task.error_message = str(e)
            db.session.commit()

@visual_bp.route('/tasks/<int:task_id>', methods=['GET'])
@cross_origin()
def get_task_status(task_id):
    """الحصول على حالة المهمة"""
    task = GenerationTask.query.get_or_404(task_id)
    return jsonify(task.to_dict())

@visual_bp.route('/tasks', methods=['GET'])
@cross_origin()
def get_tasks():
    """الحصول على جميع المهام"""
    movie_id = request.args.get('movie_id')
    task_type = request.args.get('task_type')
    
    query = GenerationTask.query
    
    if movie_id:
        query = query.filter_by(movie_id=movie_id)
    if task_type:
        query = query.filter_by(task_type=task_type)
    
    tasks = query.order_by(GenerationTask.created_at.desc()).all()
    return jsonify([task.to_dict() for task in tasks])

@visual_bp.route('/files/<path:filename>')
@cross_origin()
def serve_generated_file(filename):
    """تقديم الملفات المولدة"""
    try:
        file_path = os.path.join(GENERATED_FILES_DIR, filename)
        if os.path.exists(file_path):
            return send_file(file_path)
        else:
            return jsonify({'error': 'File not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

