import os
import torch
from diffusers import StableDiffusionPipeline, DiffusionPipeline
from PIL import Image
import requests
from io import BytesIO
import json
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ImageGenerator:
    def __init__(self):
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.models = {}
        self.current_model = None
        
    def load_model(self, model_name="runwayml/stable-diffusion-v1-5"):
        """تحميل نموذج توليد الصور"""
        try:
            if model_name not in self.models:
                logger.info(f"Loading model: {model_name}")
                
                # تحميل النموذج مع تحسينات الذاكرة
                pipe = StableDiffusionPipeline.from_pretrained(
                    model_name,
                    torch_dtype=torch.float16 if self.device == "cuda" else torch.float32,
                    safety_checker=None,
                    requires_safety_checker=False
                )
                
                pipe = pipe.to(self.device)
                
                # تحسينات الذاكرة
                if self.device == "cuda":
                    pipe.enable_memory_efficient_attention()
                    pipe.enable_xformers_memory_efficient_attention()
                
                self.models[model_name] = pipe
                self.current_model = model_name
                logger.info(f"Model {model_name} loaded successfully")
                
            return True
        except Exception as e:
            logger.error(f"Error loading model {model_name}: {str(e)}")
            return False
    
    def generate_image(self, prompt, negative_prompt="", width=512, height=512, 
                      num_inference_steps=20, guidance_scale=7.5, seed=None):
        """توليد صورة من النص"""
        try:
            if not self.current_model or self.current_model not in self.models:
                # تحميل النموذج الافتراضي
                if not self.load_model():
                    raise Exception("Failed to load default model")
            
            pipe = self.models[self.current_model]
            
            # تعيين البذرة للحصول على نتائج قابلة للتكرار
            if seed is not None:
                generator = torch.Generator(device=self.device).manual_seed(seed)
            else:
                generator = None
            
            # تحسين الـ prompt للثقافة العربية
            enhanced_prompt = self.enhance_prompt_for_arabic_culture(prompt)
            
            # توليد الصورة
            logger.info(f"Generating image with prompt: {enhanced_prompt}")
            
            with torch.autocast(self.device):
                result = pipe(
                    prompt=enhanced_prompt,
                    negative_prompt=negative_prompt + ", nsfw, inappropriate, explicit",
                    width=width,
                    height=height,
                    num_inference_steps=num_inference_steps,
                    guidance_scale=guidance_scale,
                    generator=generator
                )
            
            image = result.images[0]
            return image
            
        except Exception as e:
            logger.error(f"Error generating image: {str(e)}")
            raise e
    
    def enhance_prompt_for_arabic_culture(self, prompt):
        """تحسين الـ prompt ليناسب الثقافة العربية"""
        # إضافة كلمات مفتاحية للثقافة العربية والإسلامية
        cultural_enhancements = [
            "respectful", "family-friendly", "culturally appropriate",
            "modest", "traditional values", "clean", "wholesome"
        ]
        
        # إضافة التحسينات إلى الـ prompt
        enhanced = f"{prompt}, {', '.join(cultural_enhancements)}"
        
        return enhanced
    
    def save_image(self, image, file_path):
        """حفظ الصورة في مسار محدد"""
        try:
            # إنشاء المجلد إذا لم يكن موجوداً
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            
            # حفظ الصورة
            image.save(file_path, quality=95)
            logger.info(f"Image saved to: {file_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error saving image: {str(e)}")
            return False
    
    def generate_character_image(self, character_description, style="realistic"):
        """توليد صورة شخصية بناءً على الوصف"""
        style_prompts = {
            "realistic": "photorealistic, high quality, detailed",
            "cartoon": "cartoon style, animated, colorful",
            "anime": "anime style, manga, japanese animation",
            "artistic": "artistic, painting style, creative"
        }
        
        style_prompt = style_prompts.get(style, style_prompts["realistic"])
        full_prompt = f"{character_description}, {style_prompt}"
        
        return self.generate_image(full_prompt)
    
    def generate_scene_image(self, scene_description, mood="neutral"):
        """توليد صورة مشهد بناءً على الوصف"""
        mood_prompts = {
            "happy": "bright, cheerful, positive atmosphere",
            "sad": "melancholic, somber, emotional",
            "dramatic": "dramatic lighting, intense, cinematic",
            "peaceful": "calm, serene, peaceful atmosphere",
            "action": "dynamic, energetic, action-packed",
            "neutral": "balanced lighting, natural atmosphere"
        }
        
        mood_prompt = mood_prompts.get(mood, mood_prompts["neutral"])
        full_prompt = f"{scene_description}, {mood_prompt}, cinematic quality"
        
        return self.generate_image(full_prompt)
    
    def cleanup_models(self):
        """تنظيف الذاكرة من النماذج"""
        for model_name in list(self.models.keys()):
            del self.models[model_name]
        
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
        
        self.models = {}
        self.current_model = None
        logger.info("Models cleaned up from memory")

# إنشاء مثيل عام للاستخدام
image_generator = ImageGenerator()

