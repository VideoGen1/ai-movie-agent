import os
import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from moviepy.editor import *
import json
import logging
import requests
from datetime import datetime
import tempfile

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MovieEditor:
    def __init__(self):
        self.temp_dir = tempfile.mkdtemp()
        self.default_resolution = (1920, 1080)
        self.default_fps = 24
        
    def create_movie_from_timeline(self, timeline_data, output_path, settings=None):
        """إنشاء فيلم من بيانات الخط الزمني"""
        try:
            if not settings:
                settings = {
                    'resolution': self.default_resolution,
                    'fps': self.default_fps,
                    'quality': 'high'
                }
            
            # تجميع العناصر حسب الطبقات
            layers = {}
            for item in timeline_data:
                layer = item.get('layer', 1)
                if layer not in layers:
                    layers[layer] = []
                layers[layer].append(item)
            
            # إنشاء مقاطع الفيديو لكل طبقة
            layer_clips = []
            for layer_num in sorted(layers.keys()):
                layer_clip = self.create_layer_clip(layers[layer_num], settings)
                if layer_clip:
                    layer_clips.append(layer_clip)
            
            # دمج الطبقات
            if layer_clips:
                final_clip = CompositeVideoClip(layer_clips)
                
                # تطبيق الإعدادات النهائية
                final_clip = final_clip.set_fps(settings['fps'])
                
                # تصدير الفيديو
                codec = 'libx264'
                audio_codec = 'aac'
                
                if settings['quality'] == 'ultra':
                    bitrate = '8000k'
                elif settings['quality'] == 'high':
                    bitrate = '4000k'
                elif settings['quality'] == 'medium':
                    bitrate = '2000k'
                else:  # low
                    bitrate = '1000k'
                
                final_clip.write_videofile(
                    output_path,
                    codec=codec,
                    audio_codec=audio_codec,
                    bitrate=bitrate,
                    temp_audiofile=os.path.join(self.temp_dir, 'temp_audio.m4a'),
                    remove_temp=True
                )
                
                # تنظيف الذاكرة
                final_clip.close()
                for clip in layer_clips:
                    clip.close()
                
                return True
            else:
                logger.error("No valid clips created")
                return False
                
        except Exception as e:
            logger.error(f"Error creating movie: {str(e)}")
            return False
    
    def create_layer_clip(self, layer_items, settings):
        """إنشاء مقطع فيديو لطبقة واحدة"""
        try:
            clips = []
            
            for item in layer_items:
                clip = self.create_clip_from_item(item, settings)
                if clip:
                    clips.append(clip)
            
            if clips:
                # ترتيب المقاطع حسب وقت البداية
                clips.sort(key=lambda x: x.start)
                
                # دمج المقاطع في الطبقة
                layer_clip = concatenate_videoclips(clips, method="compose")
                return layer_clip
            
            return None
            
        except Exception as e:
            logger.error(f"Error creating layer clip: {str(e)}")
            return None
    
    def create_clip_from_item(self, item, settings):
        """إنشاء مقطع فيديو من عنصر واحد"""
        try:
            element_type = item.get('element_type')
            start_time = item.get('start_time', 0)
            end_time = item.get('end_time', 5)
            duration = end_time - start_time
            
            if element_type == 'image':
                return self.create_image_clip(item, duration, settings)
            elif element_type == 'video':
                return self.create_video_clip(item, start_time, end_time, settings)
            elif element_type == 'audio':
                return self.create_audio_clip(item, start_time, end_time, settings)
            elif element_type == 'text':
                return self.create_text_clip(item, duration, settings)
            else:
                logger.warning(f"Unknown element type: {element_type}")
                return None
                
        except Exception as e:
            logger.error(f"Error creating clip from item: {str(e)}")
            return None
    
    def create_image_clip(self, item, duration, settings):
        """إنشاء مقطع فيديو من صورة"""
        try:
            # الحصول على مسار الصورة
            image_path = self.get_asset_path(item)
            if not image_path or not os.path.exists(image_path):
                return None
            
            # إنشاء مقطع الصورة
            clip = ImageClip(image_path, duration=duration)
            
            # تطبيق التحويلات
            clip = self.apply_transformations(clip, item, settings)
            
            # تعيين وقت البداية
            clip = clip.set_start(item.get('start_time', 0))
            
            return clip
            
        except Exception as e:
            logger.error(f"Error creating image clip: {str(e)}")
            return None
    
    def create_video_clip(self, item, start_time, end_time, settings):
        """إنشاء مقطع فيديو من فيديو"""
        try:
            # الحصول على مسار الفيديو
            video_path = self.get_asset_path(item)
            if not video_path or not os.path.exists(video_path):
                return None
            
            # إنشاء مقطع الفيديو
            clip = VideoFileClip(video_path)
            
            # قص الفيديو حسب الوقت المطلوب
            duration = end_time - start_time
            if duration < clip.duration:
                clip = clip.subclip(0, duration)
            
            # تطبيق التحويلات
            clip = self.apply_transformations(clip, item, settings)
            
            # تعيين وقت البداية
            clip = clip.set_start(start_time)
            
            return clip
            
        except Exception as e:
            logger.error(f"Error creating video clip: {str(e)}")
            return None
    
    def create_audio_clip(self, item, start_time, end_time, settings):
        """إنشاء مقطع صوتي"""
        try:
            # الحصول على مسار الصوت
            audio_path = self.get_asset_path(item)
            if not audio_path or not os.path.exists(audio_path):
                return None
            
            # إنشاء مقطع الصوت
            audio_clip = AudioFileClip(audio_path)
            
            # قص الصوت حسب الوقت المطلوب
            duration = end_time - start_time
            if duration < audio_clip.duration:
                audio_clip = audio_clip.subclip(0, duration)
            
            # إنشاء فيديو صامت بنفس المدة
            video_clip = ColorClip(
                size=settings['resolution'], 
                color=(0, 0, 0), 
                duration=duration
            ).set_audio(audio_clip)
            
            # تعيين وقت البداية
            video_clip = video_clip.set_start(start_time)
            
            return video_clip
            
        except Exception as e:
            logger.error(f"Error creating audio clip: {str(e)}")
            return None
    
    def create_text_clip(self, item, duration, settings):
        """إنشاء مقطع نصي"""
        try:
            text_content = item.get('text_content', 'نص تجريبي')
            
            # إنشاء مقطع نصي
            clip = TextClip(
                text_content,
                fontsize=item.get('font_size', 50),
                color=item.get('color', 'white'),
                font=item.get('font', 'Arial'),
                duration=duration
            )
            
            # تطبيق التحويلات
            clip = self.apply_transformations(clip, item, settings)
            
            # تعيين وقت البداية
            clip = clip.set_start(item.get('start_time', 0))
            
            return clip
            
        except Exception as e:
            logger.error(f"Error creating text clip: {str(e)}")
            return None
    
    def apply_transformations(self, clip, item, settings):
        """تطبيق التحويلات على المقطع"""
        try:
            # تطبيق الحجم
            scale = item.get('scale', 1.0)
            if scale != 1.0:
                clip = clip.resize(scale)
            
            # تطبيق الموضع
            position_x = item.get('position_x', 0)
            position_y = item.get('position_y', 0)
            if position_x != 0 or position_y != 0:
                clip = clip.set_position((position_x, position_y))
            
            # تطبيق الشفافية
            opacity = item.get('opacity', 1.0)
            if opacity != 1.0:
                clip = clip.set_opacity(opacity)
            
            # تطبيق المؤثرات
            effects = item.get('effects')
            if effects:
                clip = self.apply_effects(clip, effects)
            
            return clip
            
        except Exception as e:
            logger.error(f"Error applying transformations: {str(e)}")
            return clip
    
    def apply_effects(self, clip, effects_json):
        """تطبيق المؤثرات على المقطع"""
        try:
            if isinstance(effects_json, str):
                effects = json.loads(effects_json)
            else:
                effects = effects_json
            
            for effect in effects:
                effect_type = effect.get('type')
                params = effect.get('params', {})
                
                if effect_type == 'fade_in':
                    duration = params.get('duration', 1.0)
                    clip = clip.fadein(duration)
                
                elif effect_type == 'fade_out':
                    duration = params.get('duration', 1.0)
                    clip = clip.fadeout(duration)
                
                elif effect_type == 'crossfade':
                    duration = params.get('duration', 1.0)
                    clip = clip.crossfadein(duration)
                
                elif effect_type == 'speed':
                    factor = params.get('factor', 1.0)
                    clip = clip.fx(speedx, factor)
                
                elif effect_type == 'blur':
                    # تأثير الضبابية (يتطلب تنفيذ مخصص)
                    pass
            
            return clip
            
        except Exception as e:
            logger.error(f"Error applying effects: {str(e)}")
            return clip
    
    def get_asset_path(self, item):
        """الحصول على مسار الملف من العنصر"""
        try:
            # هذه الدالة تحتاج للتكامل مع خدمات أخرى
            # للحصول على مسارات الملفات الفعلية
            element_id = item.get('element_id')
            element_type = item.get('element_type')
            
            # مؤقتاً، نعيد مسار وهمي
            return f"/path/to/{element_type}_{element_id}.jpg"
            
        except Exception as e:
            logger.error(f"Error getting asset path: {str(e)}")
            return None
    
    def create_preview(self, timeline_data, duration=10):
        """إنشاء معاينة سريعة للفيلم"""
        try:
            # إنشاء معاينة قصيرة (أول 10 ثوانٍ)
            preview_timeline = []
            for item in timeline_data:
                if item.get('start_time', 0) < duration:
                    preview_item = item.copy()
                    if preview_item.get('end_time', 0) > duration:
                        preview_item['end_time'] = duration
                    preview_timeline.append(preview_item)
            
            # إنشاء ملف معاينة مؤقت
            preview_path = os.path.join(self.temp_dir, 'preview.mp4')
            
            settings = {
                'resolution': (854, 480),  # دقة أقل للمعاينة
                'fps': 24,
                'quality': 'medium'
            }
            
            success = self.create_movie_from_timeline(
                preview_timeline, 
                preview_path, 
                settings
            )
            
            if success:
                return preview_path
            else:
                return None
                
        except Exception as e:
            logger.error(f"Error creating preview: {str(e)}")
            return None
    
    def get_movie_info(self, video_path):
        """الحصول على معلومات الفيديو"""
        try:
            clip = VideoFileClip(video_path)
            info = {
                'duration': clip.duration,
                'fps': clip.fps,
                'size': clip.size,
                'has_audio': clip.audio is not None
            }
            clip.close()
            return info
            
        except Exception as e:
            logger.error(f"Error getting movie info: {str(e)}")
            return None
    
    def extract_frames(self, video_path, times, output_dir):
        """استخراج إطارات من الفيديو"""
        try:
            clip = VideoFileClip(video_path)
            frame_paths = []
            
            for i, time in enumerate(times):
                if time <= clip.duration:
                    frame = clip.get_frame(time)
                    frame_path = os.path.join(output_dir, f'frame_{i:04d}.jpg')
                    
                    # تحويل إلى PIL وحفظ
                    pil_image = Image.fromarray(frame)
                    pil_image.save(frame_path, 'JPEG', quality=95)
                    frame_paths.append(frame_path)
            
            clip.close()
            return frame_paths
            
        except Exception as e:
            logger.error(f"Error extracting frames: {str(e)}")
            return []
    
    def cleanup(self):
        """تنظيف الملفات المؤقتة"""
        try:
            import shutil
            if os.path.exists(self.temp_dir):
                shutil.rmtree(self.temp_dir)
            logger.info("Temporary files cleaned up")
            
        except Exception as e:
            logger.error(f"Error cleaning up: {str(e)}")

# إنشاء مثيل عام للاستخدام
movie_editor = MovieEditor()

