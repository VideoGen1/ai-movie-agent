import os
import numpy as np
import librosa
import soundfile as sf
from gtts import gTTS
import pyttsx3
from pydub import AudioSegment
from pydub.generators import Sine, WhiteNoise
import tempfile
import logging
import json
from scipy import signal
import random

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AudioGenerator:
    def __init__(self):
        self.tts_engine = None
        self.sample_rate = 22050
        self.initialize_tts_engine()
        
    def initialize_tts_engine(self):
        """تهيئة محرك تحويل النص إلى كلام"""
        try:
            self.tts_engine = pyttsx3.init()
            
            # تعيين الخصائص الافتراضية
            voices = self.tts_engine.getProperty('voices')
            if voices:
                # البحث عن صوت عربي إن وجد
                arabic_voice = None
                for voice in voices:
                    if 'ar' in voice.id.lower() or 'arabic' in voice.name.lower():
                        arabic_voice = voice
                        break
                
                if arabic_voice:
                    self.tts_engine.setProperty('voice', arabic_voice.id)
                else:
                    # استخدام أول صوت متاح
                    self.tts_engine.setProperty('voice', voices[0].id)
            
            # تعيين سرعة الكلام
            self.tts_engine.setProperty('rate', 150)
            
            # تعيين مستوى الصوت
            self.tts_engine.setProperty('volume', 0.9)
            
            logger.info("TTS engine initialized successfully")
            
        except Exception as e:
            logger.error(f"Error initializing TTS engine: {str(e)}")
            self.tts_engine = None
    
    def text_to_speech_gtts(self, text, language='ar', slow=False):
        """تحويل النص إلى كلام باستخدام Google TTS"""
        try:
            # إنشاء ملف مؤقت
            with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as temp_file:
                temp_path = temp_file.name
            
            # تحويل النص إلى كلام
            tts = gTTS(text=text, lang=language, slow=slow)
            tts.save(temp_path)
            
            # تحويل إلى WAV
            audio = AudioSegment.from_mp3(temp_path)
            
            # حذف الملف المؤقت
            os.unlink(temp_path)
            
            return audio
            
        except Exception as e:
            logger.error(f"Error in text_to_speech_gtts: {str(e)}")
            return None
    
    def text_to_speech_pyttsx3(self, text, voice_type='default'):
        """تحويل النص إلى كلام باستخدام pyttsx3"""
        try:
            if not self.tts_engine:
                self.initialize_tts_engine()
                if not self.tts_engine:
                    return None
            
            # تعيين نوع الصوت
            voices = self.tts_engine.getProperty('voices')
            if voices and voice_type != 'default':
                for voice in voices:
                    if voice_type.lower() in voice.name.lower():
                        self.tts_engine.setProperty('voice', voice.id)
                        break
            
            # إنشاء ملف مؤقت
            with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as temp_file:
                temp_path = temp_file.name
            
            # حفظ الصوت
            self.tts_engine.save_to_file(text, temp_path)
            self.tts_engine.runAndWait()
            
            # تحميل الملف الصوتي
            audio = AudioSegment.from_wav(temp_path)
            
            # حذف الملف المؤقت
            os.unlink(temp_path)
            
            return audio
            
        except Exception as e:
            logger.error(f"Error in text_to_speech_pyttsx3: {str(e)}")
            return None
    
    def generate_background_music(self, duration_seconds, mood='neutral', tempo=120):
        """توليد موسيقى خلفية بسيطة"""
        try:
            sample_rate = self.sample_rate
            duration_samples = int(duration_seconds * sample_rate)
            
            # تحديد النغمات حسب المزاج
            mood_scales = {
                'happy': [261.63, 293.66, 329.63, 349.23, 392.00, 440.00, 493.88],  # C major
                'sad': [220.00, 246.94, 261.63, 293.66, 329.63, 349.23, 392.00],    # A minor
                'dramatic': [146.83, 164.81, 174.61, 196.00, 220.00, 246.94, 261.63], # D minor
                'peaceful': [174.61, 196.00, 220.00, 233.08, 261.63, 293.66, 329.63], # F major
                'action': [146.83, 164.81, 185.00, 196.00, 220.00, 246.94, 277.18],   # D minor pentatonic
                'neutral': [261.63, 293.66, 329.63, 349.23, 392.00, 440.00, 493.88]   # C major
            }
            
            scale = mood_scales.get(mood, mood_scales['neutral'])
            
            # إنشاء الموسيقى
            music = np.zeros(duration_samples)
            beat_duration = 60.0 / tempo  # مدة النبضة بالثواني
            beat_samples = int(beat_duration * sample_rate)
            
            # إضافة النغمات
            for i in range(0, duration_samples, beat_samples):
                if i + beat_samples > duration_samples:
                    break
                
                # اختيار نغمة عشوائية من السلم
                frequency = random.choice(scale)
                
                # إنشاء النغمة
                t = np.linspace(0, beat_duration, beat_samples)
                note = 0.3 * np.sin(2 * np.pi * frequency * t)
                
                # إضافة تأثير التلاشي
                fade_samples = int(0.1 * beat_samples)
                note[:fade_samples] *= np.linspace(0, 1, fade_samples)
                note[-fade_samples:] *= np.linspace(1, 0, fade_samples)
                
                # إضافة النغمة إلى الموسيقى
                end_idx = min(i + beat_samples, duration_samples)
                music[i:end_idx] += note[:end_idx-i]
            
            # تطبيق مرشح تمرير منخفض للحصول على صوت أكثر نعومة
            b, a = signal.butter(4, 0.3, 'low')
            music = signal.filtfilt(b, a, music)
            
            # تطبيع الصوت
            music = music / np.max(np.abs(music)) * 0.7
            
            return music, sample_rate
            
        except Exception as e:
            logger.error(f"Error generating background music: {str(e)}")
            return None, None
    
    def generate_sound_effect(self, effect_type, duration=1.0, **params):
        """توليد مؤثرات صوتية"""
        try:
            sample_rate = self.sample_rate
            duration_samples = int(duration * sample_rate)
            t = np.linspace(0, duration, duration_samples)
            
            if effect_type == 'footsteps':
                # صوت خطوات
                effect = np.zeros(duration_samples)
                step_interval = 0.5  # خطوة كل نصف ثانية
                step_samples = int(step_interval * sample_rate)
                
                for i in range(0, duration_samples, step_samples):
                    if i + int(0.1 * sample_rate) < duration_samples:
                        # صوت خطوة واحدة
                        step_duration = int(0.1 * sample_rate)
                        step_t = np.linspace(0, 0.1, step_duration)
                        step_sound = 0.5 * np.random.normal(0, 0.1, step_duration)
                        step_sound *= np.exp(-step_t * 20)  # تلاشي سريع
                        effect[i:i+step_duration] += step_sound
            
            elif effect_type == 'rain':
                # صوت مطر
                effect = 0.3 * np.random.normal(0, 0.1, duration_samples)
                # تطبيق مرشح تمرير عالي للحصول على صوت المطر
                b, a = signal.butter(4, 0.7, 'high')
                effect = signal.filtfilt(b, a, effect)
            
            elif effect_type == 'wind':
                # صوت رياح
                effect = 0.4 * np.random.normal(0, 0.1, duration_samples)
                # تطبيق مرشح تمرير منخفض
                b, a = signal.butter(4, 0.2, 'low')
                effect = signal.filtfilt(b, a, effect)
                # إضافة تذبذب
                modulation = 0.5 + 0.5 * np.sin(2 * np.pi * 0.5 * t)
                effect *= modulation
            
            elif effect_type == 'door_knock':
                # صوت طرق الباب
                effect = np.zeros(duration_samples)
                knock_times = [0.0, 0.2, 0.4]  # ثلاث طرقات
                
                for knock_time in knock_times:
                    knock_start = int(knock_time * sample_rate)
                    knock_duration = int(0.1 * sample_rate)
                    
                    if knock_start + knock_duration < duration_samples:
                        knock_t = np.linspace(0, 0.1, knock_duration)
                        knock_sound = 0.8 * np.sin(2 * np.pi * 200 * knock_t)
                        knock_sound *= np.exp(-knock_t * 30)
                        effect[knock_start:knock_start+knock_duration] += knock_sound
            
            elif effect_type == 'applause':
                # صوت تصفيق
                effect = 0.6 * np.random.normal(0, 0.2, duration_samples)
                # إضافة تذبذب للتصفيق
                modulation = 0.7 + 0.3 * np.sin(2 * np.pi * 8 * t)
                effect *= modulation
            
            else:
                # مؤثر افتراضي (ضوضاء بيضاء)
                effect = 0.2 * np.random.normal(0, 0.1, duration_samples)
            
            # تطبيع الصوت
            if np.max(np.abs(effect)) > 0:
                effect = effect / np.max(np.abs(effect)) * 0.8
            
            return effect, sample_rate
            
        except Exception as e:
            logger.error(f"Error generating sound effect: {str(e)}")
            return None, None
    
    def mix_audio(self, audio_tracks, volumes=None):
        """خلط عدة مسارات صوتية"""
        try:
            if not audio_tracks:
                return None
            
            if volumes is None:
                volumes = [1.0] * len(audio_tracks)
            
            # تحديد أطول مسار
            max_length = max(len(track) for track in audio_tracks)
            
            # خلط المسارات
            mixed = np.zeros(max_length)
            
            for i, (track, volume) in enumerate(zip(audio_tracks, volumes)):
                # تمديد المسار إذا كان أقصر
                if len(track) < max_length:
                    track = np.pad(track, (0, max_length - len(track)), 'constant')
                
                mixed += track * volume
            
            # تطبيع الصوت النهائي
            if np.max(np.abs(mixed)) > 0:
                mixed = mixed / np.max(np.abs(mixed)) * 0.9
            
            return mixed
            
        except Exception as e:
            logger.error(f"Error mixing audio: {str(e)}")
            return None
    
    def save_audio(self, audio_data, file_path, sample_rate=None):
        """حفظ البيانات الصوتية في ملف"""
        try:
            if sample_rate is None:
                sample_rate = self.sample_rate
            
            # إنشاء المجلد إذا لم يكن موجوداً
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            
            # حفظ الملف
            if isinstance(audio_data, AudioSegment):
                audio_data.export(file_path, format="wav")
            else:
                sf.write(file_path, audio_data, sample_rate)
            
            logger.info(f"Audio saved to: {file_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error saving audio: {str(e)}")
            return False
    
    def get_audio_info(self, file_path):
        """الحصول على معلومات الملف الصوتي"""
        try:
            audio_data, sample_rate = librosa.load(file_path, sr=None)
            duration = len(audio_data) / sample_rate
            
            return {
                'duration': duration,
                'sample_rate': sample_rate,
                'channels': 1 if audio_data.ndim == 1 else audio_data.shape[0],
                'samples': len(audio_data)
            }
            
        except Exception as e:
            logger.error(f"Error getting audio info: {str(e)}")
            return None
    
    def apply_effects(self, audio_data, effects):
        """تطبيق مؤثرات على الصوت"""
        try:
            processed_audio = audio_data.copy()
            
            for effect in effects:
                effect_type = effect.get('type')
                params = effect.get('params', {})
                
                if effect_type == 'reverb':
                    # تأثير الصدى
                    delay = params.get('delay', 0.1)
                    decay = params.get('decay', 0.3)
                    delay_samples = int(delay * self.sample_rate)
                    
                    reverb = np.zeros_like(processed_audio)
                    if delay_samples < len(processed_audio):
                        reverb[delay_samples:] = processed_audio[:-delay_samples] * decay
                        processed_audio += reverb
                
                elif effect_type == 'echo':
                    # تأثير الصدى المتكرر
                    delay = params.get('delay', 0.3)
                    decay = params.get('decay', 0.5)
                    delay_samples = int(delay * self.sample_rate)
                    
                    echo = np.zeros_like(processed_audio)
                    if delay_samples < len(processed_audio):
                        echo[delay_samples:] = processed_audio[:-delay_samples] * decay
                        processed_audio += echo
                
                elif effect_type == 'fade_in':
                    # تأثير الظهور التدريجي
                    fade_duration = params.get('duration', 1.0)
                    fade_samples = int(fade_duration * self.sample_rate)
                    fade_samples = min(fade_samples, len(processed_audio))
                    
                    fade_curve = np.linspace(0, 1, fade_samples)
                    processed_audio[:fade_samples] *= fade_curve
                
                elif effect_type == 'fade_out':
                    # تأثير الاختفاء التدريجي
                    fade_duration = params.get('duration', 1.0)
                    fade_samples = int(fade_duration * self.sample_rate)
                    fade_samples = min(fade_samples, len(processed_audio))
                    
                    fade_curve = np.linspace(1, 0, fade_samples)
                    processed_audio[-fade_samples:] *= fade_curve
            
            return processed_audio
            
        except Exception as e:
            logger.error(f"Error applying effects: {str(e)}")
            return audio_data

# إنشاء مثيل عام للاستخدام
audio_generator = AudioGenerator()

