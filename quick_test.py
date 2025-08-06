#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AI Movie Agent - Quick Test Script
وكيل الذكاء الاصطناعي لإنتاج الأفلام - اختبار سريع
"""

import os
import sys
import subprocess
import importlib.util

def check_file_exists(file_path, description):
    """فحص وجود ملف"""
    if os.path.exists(file_path):
        print(f"✅ {description}: {file_path}")
        return True
    else:
        print(f"❌ {description}: {file_path} (not found)")
        return False

def check_directory_structure():
    """فحص هيكل المجلدات"""
    print("🔍 Checking directory structure...")
    
    required_dirs = [
        "scenario_generator",
        "visual_generator", 
        "audio_generator",
        "movie_editor",
        "ai-movie-studio"
    ]
    
    all_exist = True
    for dir_name in required_dirs:
        if os.path.exists(dir_name):
            print(f"✅ Directory: {dir_name}")
        else:
            print(f"❌ Directory: {dir_name} (missing)")
            all_exist = False
            
    return all_exist

def check_python_files():
    """فحص الملفات الأساسية لـ Python"""
    print("\n🐍 Checking Python files...")
    
    python_files = [
        "scenario_generator/src/main.py",
        "visual_generator/src/main.py",
        "audio_generator/src/main.py", 
        "movie_editor/src/main.py"
    ]
    
    all_exist = True
    for file_path in python_files:
        if not check_file_exists(file_path, "Python main file"):
            all_exist = False
            
    return all_exist

def check_requirements_files():
    """فحص ملفات المتطلبات"""
    print("\n📦 Checking requirements files...")
    
    req_files = [
        "scenario_generator/requirements.txt",
        "visual_generator/requirements.txt",
        "audio_generator/requirements.txt",
        "movie_editor/requirements.txt"
    ]
    
    all_exist = True
    for file_path in req_files:
        if not check_file_exists(file_path, "Requirements file"):
            all_exist = False
            
    return all_exist

def check_frontend_files():
    """فحص ملفات الواجهة الأمامية"""
    print("\n⚛️ Checking frontend files...")
    
    frontend_files = [
        "ai-movie-studio/package.json",
        "ai-movie-studio/src/App.jsx",
        "ai-movie-studio/index.html"
    ]
    
    all_exist = True
    for file_path in frontend_files:
        if not check_file_exists(file_path, "Frontend file"):
            all_exist = False
            
    return all_exist

def check_config_files():
    """فحص ملفات التكوين"""
    print("\n⚙️ Checking configuration files...")
    
    config_files = [
        ".gitpod.yml",
        "docker-compose.yml",
        "README.md",
        "LICENSE",
        ".env.example"
    ]
    
    all_exist = True
    for file_path in config_files:
        if not check_file_exists(file_path, "Config file"):
            all_exist = False
            
    return all_exist

def check_scripts():
    """فحص السكريپتات"""
    print("\n📜 Checking scripts...")
    
    scripts = [
        "start_services.sh",
        "stop_services.sh",
        "test_system.py"
    ]
    
    all_exist = True
    for script_path in scripts:
        if check_file_exists(script_path, "Script"):
            # فحص صلاحيات التنفيذ
            if os.access(script_path, os.X_OK):
                print(f"   ✅ Executable permissions: {script_path}")
            else:
                print(f"   ⚠️ Not executable: {script_path}")
        else:
            all_exist = False
            
    return all_exist

def check_python_imports():
    """فحص إمكانية استيراد المكتبات الأساسية"""
    print("\n🔬 Checking Python imports...")
    
    required_modules = [
        "flask",
        "flask_cors", 
        "requests",
        "sqlite3",
        "json",
        "os",
        "datetime"
    ]
    
    all_available = True
    for module_name in required_modules:
        try:
            if module_name == "flask_cors":
                import flask_cors
            else:
                __import__(module_name)
            print(f"✅ Module: {module_name}")
        except ImportError:
            print(f"❌ Module: {module_name} (not available)")
            all_available = False
            
    return all_available

def check_node_setup():
    """فحص إعداد Node.js"""
    print("\n🟢 Checking Node.js setup...")
    
    try:
        # فحص Node.js
        node_version = subprocess.check_output(["node", "--version"], text=True).strip()
        print(f"✅ Node.js: {node_version}")
        
        # فحص npm
        npm_version = subprocess.check_output(["npm", "--version"], text=True).strip()
        print(f"✅ npm: {npm_version}")
        
        # فحص node_modules
        if os.path.exists("ai-movie-studio/node_modules"):
            print("✅ Frontend dependencies: installed")
        else:
            print("⚠️ Frontend dependencies: not installed")
            
        return True
        
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("❌ Node.js or npm not available")
        return False

def check_virtual_environments():
    """فحص البيئات الافتراضية لـ Python"""
    print("\n🐍 Checking Python virtual environments...")
    
    services = ["scenario_generator", "visual_generator", "audio_generator", "movie_editor"]
    
    all_exist = True
    for service in services:
        venv_path = f"{service}/venv"
        if os.path.exists(venv_path):
            print(f"✅ Virtual environment: {service}")
        else:
            print(f"❌ Virtual environment: {service} (missing)")
            all_exist = False
            
    return all_exist

def generate_report():
    """إنشاء تقرير شامل"""
    print("\n" + "="*60)
    print("🎬 AI Movie Agent - Quick Test Report")
    print("="*60)
    
    tests = [
        ("Directory Structure", check_directory_structure()),
        ("Python Files", check_python_files()),
        ("Requirements Files", check_requirements_files()),
        ("Frontend Files", check_frontend_files()),
        ("Configuration Files", check_config_files()),
        ("Scripts", check_scripts()),
        ("Python Imports", check_python_imports()),
        ("Node.js Setup", check_node_setup()),
        ("Virtual Environments", check_virtual_environments())
    ]
    
    print("\n📊 Test Results Summary:")
    print("-" * 40)
    
    passed = 0
    total = len(tests)
    
    for test_name, result in tests:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {test_name}")
        if result:
            passed += 1
    
    print("-" * 40)
    print(f"📈 Overall Score: {passed}/{total} ({(passed/total)*100:.1f}%)")
    
    if passed == total:
        print("\n🎉 All tests passed! System is ready to run.")
        return True
    elif passed >= total * 0.8:
        print("\n⚠️ Most tests passed. System should work with minor issues.")
        return True
    else:
        print("\n❌ Multiple issues found. System may not work properly.")
        return False

def main():
    """الدالة الرئيسية"""
    print("🔍 AI Movie Agent - Quick System Check")
    print("=====================================")
    
    success = generate_report()
    
    if success:
        print("\n💡 Next steps:")
        print("   1. Run: ./start_services.sh")
        print("   2. Wait for all services to start")
        print("   3. Open: http://localhost:5173")
        print("   4. Test the system functionality")
    else:
        print("\n🔧 Recommended actions:")
        print("   1. Check missing files and directories")
        print("   2. Install missing dependencies")
        print("   3. Run setup scripts if available")
        print("   4. Re-run this test")
    
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

