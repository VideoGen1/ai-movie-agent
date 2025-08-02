from flask import Blueprint, jsonify, request, send_file
from flask_cors import cross_origin
from src.models.audio_content import AudioContent, AudioTask, VoiceProfile, db
from src.services.audio_generator import audio_generator
import json
import os
import uuid
from datetime import datetime
import threading
import logging
import numpy as np

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

audio_bp = Blueprint('audio', __name__)

# مجلد حفظ الملفات المولدة
GENERATED_AUDIO_DIR = os.path.join(os.path.dirname(__file__), '..', 'generated_audio')
os.makedirs(GENERATED_AUDIO_DIR, exist_ok=True)

@audio_bp.route('/audio-content', methods=['GET'])
@cross_origin()
def get_audio_content():
    """الحصول على جميع المحتوى الصوتي"""
    movie_id = request.args.get('movie_id')
    scene_id = request.args.get('scene_id')
    content_type = request.args.get('content_type')
    
    query = AudioContent.query
    
    if movie_id:
        query = query.filter_by(movie_id=movie_id)
    if scene_id:
        query = query.filter_by(scene_id=scene_id)
    if content_type:
        query = query.filter_by(content_type=content_type)
    
    content = query.all()
    return jsonify([item.to_dict() for item in content])

@audio_bp.route('/audio-content', methods=['POST'])
@cross_origin()
def create_audio_content():
    """إنشاء محتوى صوتي جديد"""
    data = request.json
    
    content = AudioContent(
        movie_id=data.get('movie_id'),
        scene_id=data.get('scene_id'),
        content_type=data.get('content_type', 'voice'),
        title=data.get('title'),
        description=data.get('description'),
        text_content=data.get('text_content'),
        voice_type=data.get('voice_type'),
        language=data.get('language', 'ar')
    )
    
    db.session.add(content)
    db.session.commit()
    
    return jsonify(content.to_dict()), 201

@audio_bp.route('/text-to-speech', methods=['POST'])
@cross_origin()
def text_to_speech():
    """تحويل النص إلى كلام"""
    try:
        data = request.json
        text = data.get('text', '')
        movie_id = data.get('movie_id')
        scene_id = data.get('scene_id')
        voice_type = data.get('voice_type', 'default')
        language = data.get('language', 'ar')
        engine = data.get('engine', 'gtts')  # gtts أو pyttsx3
        
        if not text:
            return jsonify({'success': False, 'error': 'Text is required'}), 400
        
        # إنشاء مهمة توليد
        task = AudioTask(
            task_type='tts',
            movie_id=movie_id,
            scene_id=scene_id,
            text_content=text,
            parameters=json.dumps({
                'voice_type': voice_type,
                'language': language,
                'engine': engine
            }),
            status='processing'
        )
        db.session.add(task)
        db.session.commit()
        
        # بدء توليد الصوت في خيط منفصل
        thread = threading.Thread(
            target=generate_tts_async,
            args=(task.id, text, voice_type, language, engine)
        )
        thread.start()
        
        return jsonify({
            'success': True,
            'task_id': task.id,
            'message': 'Text-to-speech generation started'
        })
        
    except Exception as e:
        logger.error(f"Error in text_to_speech: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

def generate_tts_async(task_id, text, voice_type, language, engine):
    """توليد الصوت من النص بشكل غير متزامن"""
    try:
        task = AudioTask.query.get(task_id)
        if not task:
            return
        
        task.progress = 20
        db.session.commit()
        
        # توليد الصوت
        if engine == 'gtts':
            audio = audio_generator.text_to_speech_gtts(text, language)
        else:
            audio = audio_generator.text_to_speech_pyttsx3(text, voice_type)
        
        if not audio:
            task.status = 'failed'
            task.error_message = 'Failed to generate speech'
            db.session.commit()
            return
        
        task.progress = 80
        db.session.commit()
        
        # حفظ الملف الصوتي
        filename = f"tts_{task_id}_{uuid.uuid4().hex[:8]}.wav"
        file_path = os.path.join(GENERATED_AUDIO_DIR, filename)
        
        if audio_generator.save_audio(audio, file_path):
            # الحصول على معلومات الصوت
            audio_info = audio_generator.get_audio_info(file_path)
            
            # إنشاء سجل المحتوى الصوتي
            audio_content = AudioContent(
                movie_id=task.movie_id,
                scene_id=task.scene_id,
                content_type='voice',
                title=f"Generated Speech - {task_id}",
                text_content=text,
                file_path=file_path,
                duration=audio_info.get('duration') if audio_info else None,
                sample_rate=audio_info.get('sample_rate') if audio_info else None,
                channels=audio_info.get('channels') if audio_info else None,
                voice_type=voice_type,
                language=language,
                model_used=engine,
                generation_params=task.parameters,
                status='completed'
            )
            db.session.add(audio_content)
            
            # تحديث المهمة
            task.status = 'completed'
            task.result_path = file_path
            task.progress = 100
            db.session.commit()
            
            logger.info(f"TTS generation completed for task {task_id}")
        else:
            task.status = 'failed'
            task.error_message = 'Failed to save generated audio'
            db.session.commit()
            
    except Exception as e:
        logger.error(f"Error in generate_tts_async: {str(e)}")
        task = AudioTask.query.get(task_id)
        if task:
            task.status = 'failed'
            task.error_message = str(e)
            db.session.commit()

@audio_bp.route('/generate-music', methods=['POST'])
@cross_origin()
def generate_music():
    """توليد موسيقى خلفية"""
    try:
        data = request.json
        duration = data.get('duration', 30)  # المدة بالثواني
        mood = data.get('mood', 'neutral')
        tempo = data.get('tempo', 120)
        movie_id = data.get('movie_id')
        scene_id = data.get('scene_id')
        
        # إنشاء مهمة توليد
        task = AudioTask(
            task_type='music',
            movie_id=movie_id,
            scene_id=scene_id,
            parameters=json.dumps({
                'duration': duration,
                'mood': mood,
                'tempo': tempo
            }),
            status='processing'
        )
        db.session.add(task)
        db.session.commit()
        
        # بدء توليد الموسيقى في خيط منفصل
        thread = threading.Thread(
            target=generate_music_async,
            args=(task.id, duration, mood, tempo)
        )
        thread.start()
        
        return jsonify({
            'success': True,
            'task_id': task.id,
            'message': 'Music generation started'
        })
        
    except Exception as e:
        logger.error(f"Error in generate_music: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

def generate_music_async(task_id, duration, mood, tempo):
    """توليد الموسيقى بشكل غير متزامن"""
    try:
        task = AudioTask.query.get(task_id)
        if not task:
            return
        
        task.progress = 30
        db.session.commit()
        
        # توليد الموسيقى
        music_data, sample_rate = audio_generator.generate_background_music(
            duration, mood, tempo
        )
        
        if music_data is None:
            task.status = 'failed'
            task.error_message = 'Failed to generate music'
            db.session.commit()
            return
        
        task.progress = 80
        db.session.commit()
        
        # حفظ الملف الصوتي
        filename = f"music_{task_id}_{uuid.uuid4().hex[:8]}.wav"
        file_path = os.path.join(GENERATED_AUDIO_DIR, filename)
        
        if audio_generator.save_audio(music_data, file_path, sample_rate):
            # إنشاء سجل المحتوى الصوتي
            audio_content = AudioContent(
                movie_id=task.movie_id,
                scene_id=task.scene_id,
                content_type='music',
                title=f"Generated Music - {mood.title()}",
                description=f"Background music with {mood} mood, {tempo} BPM",
                file_path=file_path,
                duration=duration,
                sample_rate=sample_rate,
                channels=1,
                model_used='synthetic',
                generation_params=task.parameters,
                status='completed'
            )
            db.session.add(audio_content)
            
            # تحديث المهمة
            task.status = 'completed'
            task.result_path = file_path
            task.progress = 100
            db.session.commit()
            
            logger.info(f"Music generation completed for task {task_id}")
        else:
            task.status = 'failed'
            task.error_message = 'Failed to save generated music'
            db.session.commit()
            
    except Exception as e:
        logger.error(f"Error in generate_music_async: {str(e)}")
        task = AudioTask.query.get(task_id)
        if task:
            task.status = 'failed'
            task.error_message = str(e)
            db.session.commit()

@audio_bp.route('/generate-sound-effect', methods=['POST'])
@cross_origin()
def generate_sound_effect():
    """توليد مؤثرات صوتية"""
    try:
        data = request.json
        effect_type = data.get('effect_type', 'footsteps')
        duration = data.get('duration', 2.0)
        movie_id = data.get('movie_id')
        scene_id = data.get('scene_id')
        params = data.get('params', {})
        
        # إنشاء مهمة توليد
        task = AudioTask(
            task_type='sound_effect',
            movie_id=movie_id,
            scene_id=scene_id,
            parameters=json.dumps({
                'effect_type': effect_type,
                'duration': duration,
                'params': params
            }),
            status='processing'
        )
        db.session.add(task)
        db.session.commit()
        
        # بدء توليد المؤثر الصوتي في خيط منفصل
        thread = threading.Thread(
            target=generate_sound_effect_async,
            args=(task.id, effect_type, duration, params)
        )
        thread.start()
        
        return jsonify({
            'success': True,
            'task_id': task.id,
            'message': 'Sound effect generation started'
        })
        
    except Exception as e:
        logger.error(f"Error in generate_sound_effect: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

def generate_sound_effect_async(task_id, effect_type, duration, params):
    """توليد المؤثر الصوتي بشكل غير متزامن"""
    try:
        task = AudioTask.query.get(task_id)
        if not task:
            return
        
        task.progress = 30
        db.session.commit()
        
        # توليد المؤثر الصوتي
        effect_data, sample_rate = audio_generator.generate_sound_effect(
            effect_type, duration, **params
        )
        
        if effect_data is None:
            task.status = 'failed'
            task.error_message = 'Failed to generate sound effect'
            db.session.commit()
            return
        
        task.progress = 80
        db.session.commit()
        
        # حفظ الملف الصوتي
        filename = f"effect_{effect_type}_{task_id}_{uuid.uuid4().hex[:8]}.wav"
        file_path = os.path.join(GENERATED_AUDIO_DIR, filename)
        
        if audio_generator.save_audio(effect_data, file_path, sample_rate):
            # إنشاء سجل المحتوى الصوتي
            audio_content = AudioContent(
                movie_id=task.movie_id,
                scene_id=task.scene_id,
                content_type='sound_effect',
                title=f"Sound Effect - {effect_type.title()}",
                description=f"Generated {effect_type} sound effect",
                file_path=file_path,
                duration=duration,
                sample_rate=sample_rate,
                channels=1,
                model_used='synthetic',
                generation_params=task.parameters,
                status='completed'
            )
            db.session.add(audio_content)
            
            # تحديث المهمة
            task.status = 'completed'
            task.result_path = file_path
            task.progress = 100
            db.session.commit()
            
            logger.info(f"Sound effect generation completed for task {task_id}")
        else:
            task.status = 'failed'
            task.error_message = 'Failed to save generated sound effect'
            db.session.commit()
            
    except Exception as e:
        logger.error(f"Error in generate_sound_effect_async: {str(e)}")
        task = AudioTask.query.get(task_id)
        if task:
            task.status = 'failed'
            task.error_message = str(e)
            db.session.commit()

@audio_bp.route('/mix-audio', methods=['POST'])
@cross_origin()
def mix_audio():
    """خلط عدة مسارات صوتية"""
    try:
        data = request.json
        audio_ids = data.get('audio_ids', [])
        volumes = data.get('volumes', [])
        movie_id = data.get('movie_id')
        scene_id = data.get('scene_id')
        
        if not audio_ids:
            return jsonify({'success': False, 'error': 'Audio IDs are required'}), 400
        
        # إنشاء مهمة خلط
        task = AudioTask(
            task_type='mix',
            movie_id=movie_id,
            scene_id=scene_id,
            parameters=json.dumps({
                'audio_ids': audio_ids,
                'volumes': volumes
            }),
            status='processing'
        )
        db.session.add(task)
        db.session.commit()
        
        # بدء خلط الصوت في خيط منفصل
        thread = threading.Thread(
            target=mix_audio_async,
            args=(task.id, audio_ids, volumes)
        )
        thread.start()
        
        return jsonify({
            'success': True,
            'task_id': task.id,
            'message': 'Audio mixing started'
        })
        
    except Exception as e:
        logger.error(f"Error in mix_audio: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

def mix_audio_async(task_id, audio_ids, volumes):
    """خلط الصوت بشكل غير متزامن"""
    try:
        task = AudioTask.query.get(task_id)
        if not task:
            return
        
        task.progress = 20
        db.session.commit()
        
        # تحميل الملفات الصوتية
        audio_tracks = []
        for audio_id in audio_ids:
            audio_content = AudioContent.query.get(audio_id)
            if audio_content and audio_content.file_path:
                import librosa
                audio_data, _ = librosa.load(audio_content.file_path, sr=audio_generator.sample_rate)
                audio_tracks.append(audio_data)
        
        if not audio_tracks:
            task.status = 'failed'
            task.error_message = 'No valid audio tracks found'
            db.session.commit()
            return
        
        task.progress = 60
        db.session.commit()
        
        # خلط المسارات
        mixed_audio = audio_generator.mix_audio(audio_tracks, volumes)
        
        if mixed_audio is None:
            task.status = 'failed'
            task.error_message = 'Failed to mix audio tracks'
            db.session.commit()
            return
        
        task.progress = 90
        db.session.commit()
        
        # حفظ الملف المخلوط
        filename = f"mixed_{task_id}_{uuid.uuid4().hex[:8]}.wav"
        file_path = os.path.join(GENERATED_AUDIO_DIR, filename)
        
        if audio_generator.save_audio(mixed_audio, file_path):
            # إنشاء سجل المحتوى الصوتي
            audio_content = AudioContent(
                movie_id=task.movie_id,
                scene_id=task.scene_id,
                content_type='mixed',
                title=f"Mixed Audio - {task_id}",
                description=f"Mixed audio from {len(audio_tracks)} tracks",
                file_path=file_path,
                duration=len(mixed_audio) / audio_generator.sample_rate,
                sample_rate=audio_generator.sample_rate,
                channels=1,
                model_used='mixer',
                generation_params=task.parameters,
                status='completed'
            )
            db.session.add(audio_content)
            
            # تحديث المهمة
            task.status = 'completed'
            task.result_path = file_path
            task.progress = 100
            db.session.commit()
            
            logger.info(f"Audio mixing completed for task {task_id}")
        else:
            task.status = 'failed'
            task.error_message = 'Failed to save mixed audio'
            db.session.commit()
            
    except Exception as e:
        logger.error(f"Error in mix_audio_async: {str(e)}")
        task = AudioTask.query.get(task_id)
        if task:
            task.status = 'failed'
            task.error_message = str(e)
            db.session.commit()

@audio_bp.route('/tasks/<int:task_id>', methods=['GET'])
@cross_origin()
def get_audio_task_status(task_id):
    """الحصول على حالة المهمة الصوتية"""
    task = AudioTask.query.get_or_404(task_id)
    return jsonify(task.to_dict())

@audio_bp.route('/tasks', methods=['GET'])
@cross_origin()
def get_audio_tasks():
    """الحصول على جميع المهام الصوتية"""
    movie_id = request.args.get('movie_id')
    task_type = request.args.get('task_type')
    
    query = AudioTask.query
    
    if movie_id:
        query = query.filter_by(movie_id=movie_id)
    if task_type:
        query = query.filter_by(task_type=task_type)
    
    tasks = query.order_by(AudioTask.created_at.desc()).all()
    return jsonify([task.to_dict() for task in tasks])

@audio_bp.route('/voice-profiles', methods=['GET'])
@cross_origin()
def get_voice_profiles():
    """الحصول على ملفات الأصوات المتاحة"""
    profiles = VoiceProfile.query.all()
    return jsonify([profile.to_dict() for profile in profiles])

@audio_bp.route('/voice-profiles', methods=['POST'])
@cross_origin()
def create_voice_profile():
    """إنشاء ملف صوتي جديد"""
    data = request.json
    
    profile = VoiceProfile(
        name=data.get('name'),
        description=data.get('description'),
        voice_type=data.get('voice_type'),
        language=data.get('language', 'ar'),
        sample_file_path=data.get('sample_file_path'),
        is_default=data.get('is_default', False)
    )
    
    db.session.add(profile)
    db.session.commit()
    
    return jsonify(profile.to_dict()), 201

@audio_bp.route('/files/<path:filename>')
@cross_origin()
def serve_audio_file(filename):
    """تقديم الملفات الصوتية المولدة"""
    try:
        file_path = os.path.join(GENERATED_AUDIO_DIR, filename)
        if os.path.exists(file_path):
            return send_file(file_path)
        else:
            return jsonify({'error': 'File not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

