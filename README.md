# 🎬 وكيل الذكاء الاصطناعي لإنتاج الأفلام

منصة شاملة لإنتاج الأفلام الطويلة باستخدام نماذج الذكاء الاصطناعي المجانية ومصادر عالية الجودة.

## 🌟 المميزات

### 🎭 إنتاج شامل للأفلام
- **توليد السيناريو**: إنشاء قصص وسيناريوهات مفصلة باستخدام GPT
- **المحتوى البصري**: توليد صور عالية الجودة باستخدام Stable Diffusion
- **المحتوى الصوتي**: تحويل النص إلى كلام وتوليد موسيقى وأصوات
- **المونتاج والتجميع**: دمج جميع العناصر في فيلم نهائي

### 🚀 تقنيات متقدمة
- **ذكاء اصطناعي مجاني 100%**: استخدام نماذج مفتوحة المصدر
- **واجهة عربية**: دعم كامل للغة العربية
- **سير عمل تلقائي**: إنتاج أفلام كاملة بنقرة واحدة
- **تصميم متجاوب**: يعمل على جميع الأجهزة

## 🏗️ المعمارية

المشروع يتكون من 5 خدمات رئيسية:

```
ai-movie-agent/
├── scenario_generator/     # خدمة توليد السيناريو (Port 5000)
├── visual_generator/       # خدمة المحتوى البصري (Port 5001)
├── audio_generator/        # خدمة المحتوى الصوتي (Port 5002)
├── movie_editor/          # خدمة المونتاج والتجميع (Port 5003)
└── ai-movie-studio/       # الواجهة الموحدة (Port 5173)
```

## 🛠️ التقنيات المستخدمة

### Backend
- **Flask**: إطار عمل Python للخدمات الخلفية
- **SQLite**: قاعدة بيانات محلية
- **OpenAI API**: لتوليد النصوص والسيناريوهات
- **Stable Diffusion**: لتوليد الصور
- **MoviePy**: لمعالجة الفيديو والمونتاج
- **gTTS & Pyttsx3**: لتحويل النص إلى كلام

### Frontend
- **React 18**: مكتبة JavaScript للواجهات
- **Tailwind CSS**: إطار عمل CSS للتصميم
- **Shadcn/UI**: مكونات UI جاهزة
- **Vite**: أداة البناء السريع

### AI Models
- **GPT-3.5/4**: توليد النصوص والسيناريوهات
- **Stable Diffusion v1.5**: توليد الصور
- **Google TTS**: تحويل النص إلى كلام

## 🚀 التشغيل السريع

### المتطلبات
- Python 3.8+
- Node.js 16+
- Git

### التثبيت

1. **استنساخ المستودع**
```bash
git clone https://github.com/your-username/ai-movie-agent.git
cd ai-movie-agent
```

2. **تشغيل خدمة السيناريو**
```bash
cd scenario_generator
python -m venv venv
source venv/bin/activate  # Linux/Mac
# أو venv\Scripts\activate  # Windows
pip install -r requirements.txt
python src/main.py
```

3. **تشغيل خدمة المحتوى البصري**
```bash
cd visual_generator
source venv/bin/activate
python src/main.py
```

4. **تشغيل خدمة المحتوى الصوتي**
```bash
cd audio_generator
source venv/bin/activate
python src/main.py
```

5. **تشغيل خدمة المونتاج**
```bash
cd movie_editor
source venv/bin/activate
python src/main.py
```

6. **تشغيل الواجهة الموحدة**
```bash
cd ai-movie-studio
npm install
npm run dev
```

### الوصول للتطبيق
- **الواجهة الموحدة**: http://localhost:5173
- **خدمة السيناريو**: http://localhost:5000
- **خدمة المحتوى البصري**: http://localhost:5001
- **خدمة المحتوى الصوتي**: http://localhost:5002
- **خدمة المونتاج**: http://localhost:5003

## 🔧 التكوين

### متغيرات البيئة
إنشاء ملف `.env` في كل خدمة:

```env
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_API_BASE=https://api.openai.com/v1
```

### إعدادات Stable Diffusion
تأكد من توفر:
- PyTorch مع دعم CUDA (للمعالجة السريعة)
- ذاكرة GPU كافية (4GB+)

## 📖 كيفية الاستخدام

### 1. إنشاء فيلم جديد
1. افتح الواجهة الموحدة
2. انقر على "مشروع جديد"
3. أدخل تفاصيل الفيلم (العنوان، النوع، الفكرة)
4. انقر على "إنشاء المشروع"

### 2. توليد السيناريو
1. انتقل إلى تبويب "السيناريو"
2. أدخل فكرة الفيلم
3. انقر على "توليد السيناريو"
4. راجع وعدل السيناريو حسب الحاجة

### 3. إنشاء المحتوى البصري
1. انتقل إلى تبويب "المحتوى البصري"
2. أدخل أوصاف المشاهد
3. اختر النمط المطلوب
4. انقر على "توليد الصور"

### 4. إنتاج المحتوى الصوتي
1. انتقل إلى تبويب "المحتوى الصوتي"
2. أدخل النصوص للتحويل إلى كلام
3. اختر نوع الصوت والموسيقى
4. انقر على "توليد الصوت"

### 5. المونتاج والتصدير
1. انتقل إلى تبويب "المونتاج"
2. رتب العناصر في الخط الزمني
3. اختر إعدادات التصدير
4. انقر على "تصدير الفيلم"

## 🌐 النشر على GitPod

### إعداد GitPod

1. **إنشاء ملف `.gitpod.yml`**
```yaml
image: gitpod/workspace-full

ports:
  - port: 5000
    onOpen: open-browser
  - port: 5001
    onOpen: ignore
  - port: 5002
    onOpen: ignore
  - port: 5003
    onOpen: ignore
  - port: 5173
    onOpen: open-browser

tasks:
  - name: Setup Backend Services
    init: |
      cd scenario_generator && python -m venv venv && source venv/bin/activate && pip install -r requirements.txt
      cd ../visual_generator && python -m venv venv && source venv/bin/activate && pip install -r requirements.txt
      cd ../audio_generator && python -m venv venv && source venv/bin/activate && pip install -r requirements.txt
      cd ../movie_editor && python -m venv venv && source venv/bin/activate && pip install -r requirements.txt
    command: |
      cd scenario_generator && source venv/bin/activate && python src/main.py &
      cd visual_generator && source venv/bin/activate && python src/main.py &
      cd audio_generator && source venv/bin/activate && python src/main.py &
      cd movie_editor && source venv/bin/activate && python src/main.py &
      wait
  
  - name: Setup Frontend
    init: cd ai-movie-studio && npm install
    command: cd ai-movie-studio && npm run dev -- --host

vscode:
  extensions:
    - ms-python.python
    - bradlc.vscode-tailwindcss
    - esbenp.prettier-vscode
```

2. **رفع إلى GitHub**
```bash
git add .
git commit -m "Initial commit: AI Movie Agent"
git branch -M main
git remote add origin https://github.com/your-username/ai-movie-agent.git
git push -u origin main
```

3. **فتح في GitPod**
- اذهب إلى: `https://gitpod.io/#https://github.com/your-username/ai-movie-agent`

## 🤝 المساهمة

نرحب بالمساهمات! يرجى اتباع الخطوات التالية:

1. Fork المستودع
2. إنشاء branch جديد (`git checkout -b feature/amazing-feature`)
3. Commit التغييرات (`git commit -m 'Add amazing feature'`)
4. Push إلى Branch (`git push origin feature/amazing-feature`)
5. فتح Pull Request

## 📄 الترخيص

هذا المشروع مرخص تحت رخصة MIT - راجع ملف [LICENSE](LICENSE) للتفاصيل.

## 🙏 شكر وتقدير

- **OpenAI** لنماذج GPT
- **Stability AI** لنماذج Stable Diffusion
- **Hugging Face** لمكتبة Transformers
- **Google** لخدمة Text-to-Speech
- **مجتمع المصادر المفتوحة** لجميع المكتبات المستخدمة

## 📞 الدعم

إذا واجهت أي مشاكل أو لديك أسئلة:

- افتح [Issue جديد](https://github.com/your-username/ai-movie-agent/issues)
- راجع [الوثائق](https://github.com/your-username/ai-movie-agent/wiki)
- تواصل معنا عبر [البريد الإلكتروني](mailto:support@example.com)

---

**صنع بـ ❤️ باستخدام الذكاء الاصطناعي المجاني**

