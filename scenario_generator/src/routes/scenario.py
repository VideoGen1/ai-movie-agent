from flask import Blueprint, jsonify, request
from flask_cors import cross_origin
from src.models.movie import Movie, Scene, Character, db
import json
import openai
import os

scenario_bp = Blueprint('scenario', __name__)

# تكوين OpenAI
openai.api_key = os.getenv('OPENAI_API_KEY')
openai.api_base = os.getenv('OPENAI_API_BASE')

@scenario_bp.route('/movies', methods=['GET'])
@cross_origin()
def get_movies():
    """الحصول على جميع الأفلام"""
    movies = Movie.query.all()
    return jsonify([movie.to_dict() for movie in movies])

@scenario_bp.route('/movies', methods=['POST'])
@cross_origin()
def create_movie():
    """إنشاء فيلم جديد"""
    data = request.json
    movie = Movie(
        title=data.get('title', 'فيلم جديد'),
        genre=data.get('genre'),
        theme=data.get('theme'),
        initial_idea=data.get('initial_idea')
    )
    db.session.add(movie)
    db.session.commit()
    return jsonify(movie.to_dict()), 201

@scenario_bp.route('/movies/<int:movie_id>', methods=['GET'])
@cross_origin()
def get_movie(movie_id):
    """الحصول على فيلم محدد"""
    movie = Movie.query.get_or_404(movie_id)
    return jsonify(movie.to_dict())

@scenario_bp.route('/movies/<int:movie_id>/generate-scenario', methods=['POST'])
@cross_origin()
def generate_scenario(movie_id):
    """توليد السيناريو للفيلم"""
    movie = Movie.query.get_or_404(movie_id)
    
    try:
        # إنشاء prompt لتوليد السيناريو
        prompt = f"""
        أنت كاتب سيناريو محترف. قم بكتابة سيناريو فيلم طويل بناءً على المعلومات التالية:

        عنوان الفيلم: {movie.title}
        النوع: {movie.genre or 'غير محدد'}
        الموضوع: {movie.theme or 'غير محدد'}
        الفكرة الأولية: {movie.initial_idea or 'غير محددة'}

        يجب أن يكون السيناريو:
        1. مناسب للثقافة العربية
        2. خالي من المشاهد المخلة
        3. يحتوي على حبكة مثيرة ومتماسكة
        4. يتضمن شخصيات متطورة وحوارات طبيعية
        5. مقسم إلى مشاهد واضحة

        اكتب السيناريو بتفصيل كامل مع وصف المشاهد والحوارات.
        """

        # استدعاء نموذج اللغة
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "أنت كاتب سيناريو محترف متخصص في الأفلام العربية."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=4000,
            temperature=0.7
        )

        scenario = response.choices[0].message.content

        # تحديث الفيلم بالسيناريو المولد
        movie.scenario = scenario
        movie.status = 'scenario_generated'
        db.session.commit()

        return jsonify({
            'success': True,
            'scenario': scenario,
            'movie': movie.to_dict()
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@scenario_bp.route('/movies/<int:movie_id>/generate-characters', methods=['POST'])
@cross_origin()
def generate_characters(movie_id):
    """توليد الشخصيات للفيلم"""
    movie = Movie.query.get_or_404(movie_id)
    
    if not movie.scenario:
        return jsonify({
            'success': False,
            'error': 'يجب توليد السيناريو أولاً'
        }), 400

    try:
        prompt = f"""
        بناءً على السيناريو التالي، قم بإنشاء قائمة مفصلة بالشخصيات الرئيسية والثانوية:

        السيناريو: {movie.scenario[:2000]}...

        لكل شخصية، قدم:
        1. الاسم
        2. الوصف الجسدي
        3. الشخصية والطباع
        4. الدور في القصة
        5. وصف الصوت المناسب

        قدم النتيجة في تنسيق JSON مع مصفوفة من الشخصيات.
        """

        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "أنت خبير في تطوير الشخصيات السينمائية."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=2000,
            temperature=0.7
        )

        characters_text = response.choices[0].message.content
        
        # محاولة تحليل JSON
        try:
            characters_data = json.loads(characters_text)
        except:
            # إذا فشل التحليل، احفظ النص كما هو
            characters_data = {"characters": [{"description": characters_text}]}

        # حفظ الشخصيات في قاعدة البيانات
        for char_data in characters_data.get('characters', []):
            character = Character(
                movie_id=movie_id,
                name=char_data.get('name', 'شخصية غير مسماة'),
                description=char_data.get('description', ''),
                personality=char_data.get('personality', ''),
                appearance=char_data.get('appearance', ''),
                voice_description=char_data.get('voice_description', ''),
                role=char_data.get('role', 'supporting')
            )
            db.session.add(character)

        movie.characters = json.dumps(characters_data, ensure_ascii=False)
        movie.status = 'characters_generated'
        db.session.commit()

        return jsonify({
            'success': True,
            'characters': characters_data,
            'movie': movie.to_dict()
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@scenario_bp.route('/movies/<int:movie_id>/generate-scenes', methods=['POST'])
@cross_origin()
def generate_scenes(movie_id):
    """تقسيم السيناريو إلى مشاهد"""
    movie = Movie.query.get_or_404(movie_id)
    
    if not movie.scenario:
        return jsonify({
            'success': False,
            'error': 'يجب توليد السيناريو أولاً'
        }), 400

    try:
        prompt = f"""
        قم بتقسيم السيناريو التالي إلى مشاهد منفصلة:

        السيناريو: {movie.scenario}

        لكل مشهد، قدم:
        1. رقم المشهد
        2. عنوان المشهد
        3. وصف المشهد
        4. الحوارات
        5. الوصف البصري
        6. الوصف الصوتي
        7. المدة المقدرة بالثواني

        قدم النتيجة في تنسيق JSON مع مصفوفة من المشاهد.
        """

        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "أنت خبير في تقسيم السيناريوهات إلى مشاهد سينمائية."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=3000,
            temperature=0.7
        )

        scenes_text = response.choices[0].message.content
        
        # محاولة تحليل JSON
        try:
            scenes_data = json.loads(scenes_text)
        except:
            # إذا فشل التحليل، احفظ النص كما هو
            scenes_data = {"scenes": [{"description": scenes_text}]}

        # حفظ المشاهد في قاعدة البيانات
        for scene_data in scenes_data.get('scenes', []):
            scene = Scene(
                movie_id=movie_id,
                scene_number=scene_data.get('scene_number', 1),
                title=scene_data.get('title', 'مشهد غير مسمى'),
                description=scene_data.get('description', ''),
                dialogue=scene_data.get('dialogue', ''),
                visual_description=scene_data.get('visual_description', ''),
                audio_description=scene_data.get('audio_description', ''),
                duration=scene_data.get('duration', 30)
            )
            db.session.add(scene)

        movie.scenes = json.dumps(scenes_data, ensure_ascii=False)
        movie.status = 'scenes_generated'
        db.session.commit()

        return jsonify({
            'success': True,
            'scenes': scenes_data,
            'movie': movie.to_dict()
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@scenario_bp.route('/movies/<int:movie_id>/characters', methods=['GET'])
@cross_origin()
def get_movie_characters(movie_id):
    """الحصول على شخصيات الفيلم"""
    characters = Character.query.filter_by(movie_id=movie_id).all()
    return jsonify([character.to_dict() for character in characters])

@scenario_bp.route('/movies/<int:movie_id>/scenes', methods=['GET'])
@cross_origin()
def get_movie_scenes(movie_id):
    """الحصول على مشاهد الفيلم"""
    scenes = Scene.query.filter_by(movie_id=movie_id).order_by(Scene.scene_number).all()
    return jsonify([scene.to_dict() for scene in scenes])

