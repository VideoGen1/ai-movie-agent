#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AI Movie Agent - System Test Script
وكيل الذكاء الاصطناعي لإنتاج الأفلام - سكريپت اختبار النظام
"""

import requests
import time
import json
import sys
import os
from datetime import datetime

class AIMovieAgentTester:
    def __init__(self):
        self.services = {
            'scenario': 'http://localhost:5000',
            'visual': 'http://localhost:5001',
            'audio': 'http://localhost:5002',
            'editor': 'http://localhost:5003',
            'frontend': 'http://localhost:5173'
        }
        self.test_results = {}
        
    def print_header(self, title):
        """طباعة عنوان مع تنسيق"""
        print(f"\n{'='*60}")
        print(f"🧪 {title}")
        print(f"{'='*60}")
        
    def print_test(self, test_name, status, details=""):
        """طباعة نتيجة اختبار"""
        status_icon = "✅" if status else "❌"
        print(f"{status_icon} {test_name}")
        if details:
            print(f"   {details}")
            
    def test_service_health(self, service_name, url):
        """اختبار صحة الخدمة"""
        try:
            response = requests.get(f"{url}/", timeout=5)
            if response.status_code == 200:
                self.print_test(f"{service_name} Service Health", True, f"Status: {response.status_code}")
                return True
            else:
                self.print_test(f"{service_name} Service Health", False, f"Status: {response.status_code}")
                return False
        except requests.exceptions.RequestException as e:
            self.print_test(f"{service_name} Service Health", False, f"Error: {str(e)}")
            return False
            
    def test_scenario_api(self):
        """اختبار واجهة برمجة التطبيقات للسيناريو"""
        try:
            # اختبار إنشاء فيلم جديد
            movie_data = {
                "title": "فيلم اختبار",
                "genre": "sci-fi",
                "theme": "التكنولوجيا والمستقبل",
                "initial_idea": "قصة عن ذكاء اصطناعي يساعد في إنتاج الأفلام"
            }
            
            response = requests.post(
                f"{self.services['scenario']}/api/movies",
                json=movie_data,
                timeout=10
            )
            
            if response.status_code == 201:
                movie = response.json()
                self.print_test("Create Movie", True, f"Movie ID: {movie.get('id')}")
                
                # اختبار توليد السيناريو
                scenario_response = requests.post(
                    f"{self.services['scenario']}/api/movies/{movie['id']}/generate-scenario",
                    timeout=30
                )
                
                if scenario_response.status_code == 200:
                    self.print_test("Generate Scenario", True, "Scenario generated successfully")
                    return True
                else:
                    self.print_test("Generate Scenario", False, f"Status: {scenario_response.status_code}")
                    return False
            else:
                self.print_test("Create Movie", False, f"Status: {response.status_code}")
                return False
                
        except requests.exceptions.RequestException as e:
            self.print_test("Scenario API", False, f"Error: {str(e)}")
            return False
            
    def test_visual_api(self):
        """اختبار واجهة برمجة التطبيقات للمحتوى البصري"""
        try:
            # اختبار توليد صورة
            image_data = {
                "description": "مشهد من فيلم خيال علمي",
                "style": "realistic",
                "movie_id": 1
            }
            
            response = requests.post(
                f"{self.services['visual']}/api/generate-image",
                json=image_data,
                timeout=15
            )
            
            if response.status_code == 200:
                result = response.json()
                self.print_test("Generate Image", True, f"Task ID: {result.get('task_id')}")
                return True
            else:
                self.print_test("Generate Image", False, f"Status: {response.status_code}")
                return False
                
        except requests.exceptions.RequestException as e:
            self.print_test("Visual API", False, f"Error: {str(e)}")
            return False
            
    def test_audio_api(self):
        """اختبار واجهة برمجة التطبيقات للمحتوى الصوتي"""
        try:
            # اختبار تحويل النص إلى كلام
            tts_data = {
                "text": "مرحباً بكم في وكيل الذكاء الاصطناعي لإنتاج الأفلام",
                "voice_type": "male",
                "movie_id": 1
            }
            
            response = requests.post(
                f"{self.services['audio']}/api/text-to-speech",
                json=tts_data,
                timeout=15
            )
            
            if response.status_code == 200:
                result = response.json()
                self.print_test("Text to Speech", True, f"Task ID: {result.get('task_id')}")
                return True
            else:
                self.print_test("Text to Speech", False, f"Status: {response.status_code}")
                return False
                
        except requests.exceptions.RequestException as e:
            self.print_test("Audio API", False, f"Error: {str(e)}")
            return False
            
    def test_editor_api(self):
        """اختبار واجهة برمجة التطبيقات للمونتاج"""
        try:
            # اختبار إنشاء مشروع
            project_data = {
                "title": "مشروع اختبار",
                "description": "مشروع لاختبار النظام",
                "genre": "test"
            }
            
            response = requests.post(
                f"{self.services['editor']}/api/projects",
                json=project_data,
                timeout=10
            )
            
            if response.status_code == 201:
                project = response.json()
                self.print_test("Create Project", True, f"Project ID: {project.get('id')}")
                return True
            else:
                self.print_test("Create Project", False, f"Status: {response.status_code}")
                return False
                
        except requests.exceptions.RequestException as e:
            self.print_test("Editor API", False, f"Error: {str(e)}")
            return False
            
    def test_integration(self):
        """اختبار التكامل بين الخدمات"""
        try:
            # اختبار مزامنة الأصول
            response = requests.post(
                f"{self.services['editor']}/api/projects/1/sync-assets",
                timeout=15
            )
            
            if response.status_code == 200:
                result = response.json()
                self.print_test("Asset Synchronization", True, f"Synced: {result.get('synced_assets', 0)} assets")
                return True
            else:
                self.print_test("Asset Synchronization", False, f"Status: {response.status_code}")
                return False
                
        except requests.exceptions.RequestException as e:
            self.print_test("Integration Test", False, f"Error: {str(e)}")
            return False
            
    def run_performance_test(self):
        """اختبار الأداء"""
        self.print_header("Performance Tests")
        
        # اختبار زمن الاستجابة
        for service_name, url in self.services.items():
            if service_name == 'frontend':
                continue
                
            try:
                start_time = time.time()
                response = requests.get(f"{url}/", timeout=5)
                end_time = time.time()
                
                response_time = (end_time - start_time) * 1000  # بالميلي ثانية
                
                if response_time < 1000:  # أقل من ثانية واحدة
                    self.print_test(f"{service_name} Response Time", True, f"{response_time:.2f}ms")
                else:
                    self.print_test(f"{service_name} Response Time", False, f"{response_time:.2f}ms (too slow)")
                    
            except requests.exceptions.RequestException as e:
                self.print_test(f"{service_name} Response Time", False, f"Error: {str(e)}")
                
    def run_all_tests(self):
        """تشغيل جميع الاختبارات"""
        print("🎬 AI Movie Agent - System Test")
        print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # اختبار صحة الخدمات
        self.print_header("Service Health Tests")
        health_results = {}
        for service_name, url in self.services.items():
            if service_name == 'frontend':
                continue  # تخطي الواجهة الأمامية في اختبار الصحة
            health_results[service_name] = self.test_service_health(service_name, url)
            
        # اختبار واجهات برمجة التطبيقات
        self.print_header("API Tests")
        api_results = {}
        
        if health_results.get('scenario', False):
            api_results['scenario'] = self.test_scenario_api()
        else:
            self.print_test("Scenario API", False, "Service not available")
            
        if health_results.get('visual', False):
            api_results['visual'] = self.test_visual_api()
        else:
            self.print_test("Visual API", False, "Service not available")
            
        if health_results.get('audio', False):
            api_results['audio'] = self.test_audio_api()
        else:
            self.print_test("Audio API", False, "Service not available")
            
        if health_results.get('editor', False):
            api_results['editor'] = self.test_editor_api()
        else:
            self.print_test("Editor API", False, "Service not available")
            
        # اختبار التكامل
        self.print_header("Integration Tests")
        if health_results.get('editor', False):
            integration_result = self.test_integration()
        else:
            self.print_test("Integration Test", False, "Editor service not available")
            integration_result = False
            
        # اختبار الأداء
        self.run_performance_test()
        
        # تلخيص النتائج
        self.print_header("Test Summary")
        
        total_tests = len(health_results) + len(api_results) + 1  # +1 للتكامل
        passed_tests = sum(health_results.values()) + sum(api_results.values()) + (1 if integration_result else 0)
        
        success_rate = (passed_tests / total_tests) * 100
        
        print(f"📊 Total Tests: {total_tests}")
        print(f"✅ Passed: {passed_tests}")
        print(f"❌ Failed: {total_tests - passed_tests}")
        print(f"📈 Success Rate: {success_rate:.1f}%")
        
        if success_rate >= 80:
            print(f"\n🎉 System is working well! ({success_rate:.1f}% success rate)")
            return True
        else:
            print(f"\n⚠️ System needs attention! ({success_rate:.1f}% success rate)")
            return False

def main():
    """الدالة الرئيسية"""
    tester = AIMovieAgentTester()
    
    print("🔍 Starting system tests...")
    print("Please make sure all services are running before proceeding.")
    
    # انتظار قصير للتأكد من تشغيل الخدمات
    print("⏳ Waiting 5 seconds for services to initialize...")
    time.sleep(5)
    
    success = tester.run_all_tests()
    
    if success:
        sys.exit(0)
    else:
        sys.exit(1)

if __name__ == "__main__":
    main()

