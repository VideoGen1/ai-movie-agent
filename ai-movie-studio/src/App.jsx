import { useState, useEffect } from 'react'
import { Button } from '@/components/ui/button.jsx'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card.jsx'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs.jsx'
import { Badge } from '@/components/ui/badge.jsx'
import { Progress } from '@/components/ui/progress.jsx'
import { Input } from '@/components/ui/input.jsx'
import { Textarea } from '@/components/ui/textarea.jsx'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select.jsx'
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog.jsx'
import { Label } from '@/components/ui/label.jsx'
import { 
  Film, 
  FileText, 
  Image, 
  Music, 
  Video, 
  Settings, 
  Play, 
  Download, 
  Upload,
  Zap,
  Sparkles,
  Camera,
  Mic,
  Edit3,
  Monitor,
  Server,
  CheckCircle,
  Clock,
  AlertCircle,
  RefreshCw
} from 'lucide-react'
import './App.css'

function App() {
  const [currentProject, setCurrentProject] = useState(null)
  const [projects, setProjects] = useState([])
  const [services, setServices] = useState({
    scenario: { status: 'unknown', url: 'http://localhost:5000' },
    visual: { status: 'unknown', url: 'http://localhost:5001' },
    audio: { status: 'unknown', url: 'http://localhost:5002' },
    editor: { status: 'unknown', url: 'http://localhost:5003' }
  })
  const [tasks, setTasks] = useState([])
  const [loading, setLoading] = useState(false)

  // فحص حالة الخدمات
  useEffect(() => {
    checkServicesStatus()
    const interval = setInterval(checkServicesStatus, 30000) // فحص كل 30 ثانية
    return () => clearInterval(interval)
  }, [])

  const checkServicesStatus = async () => {
    const newServices = { ...services }
    
    for (const [serviceName, serviceInfo] of Object.entries(services)) {
      try {
        const response = await fetch(`${serviceInfo.url}/api/`, { 
          method: 'GET',
          timeout: 5000 
        })
        newServices[serviceName].status = response.ok ? 'online' : 'offline'
      } catch (error) {
        newServices[serviceName].status = 'offline'
      }
    }
    
    setServices(newServices)
  }

  const getServiceStatusColor = (status) => {
    switch (status) {
      case 'online': return 'bg-green-500'
      case 'offline': return 'bg-red-500'
      default: return 'bg-gray-500'
    }
  }

  const getServiceStatusText = (status) => {
    switch (status) {
      case 'online': return 'متصل'
      case 'offline': return 'غير متصل'
      default: return 'غير معروف'
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-indigo-50 to-purple-50 dark:from-gray-900 dark:via-blue-900 dark:to-purple-900" dir="rtl">
      {/* Header */}
      <header className="bg-white/80 dark:bg-gray-800/80 backdrop-blur-md border-b border-gray-200 dark:border-gray-700 sticky top-0 z-50">
        <div className="container mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4 space-x-reverse">
              <div className="bg-gradient-to-r from-blue-600 to-purple-600 p-3 rounded-xl">
                <Film className="h-8 w-8 text-white" />
              </div>
              <div>
                <h1 className="text-2xl font-bold text-gray-900 dark:text-white">
                  وكيل الذكاء الاصطناعي لإنتاج الأفلام
                </h1>
                <p className="text-sm text-gray-600 dark:text-gray-300">
                  منصة شاملة لإنتاج الأفلام باستخدام الذكاء الاصطناعي
                </p>
              </div>
            </div>
            
            {/* Service Status */}
            <div className="flex items-center space-x-4 space-x-reverse">
              <div className="flex items-center space-x-2 space-x-reverse">
                <span className="text-sm text-gray-600 dark:text-gray-300">حالة الخدمات:</span>
                {Object.entries(services).map(([name, info]) => (
                  <div key={name} className="flex items-center space-x-1 space-x-reverse">
                    <div className={`w-2 h-2 rounded-full ${getServiceStatusColor(info.status)}`}></div>
                    <span className="text-xs text-gray-500 dark:text-gray-400">
                      {name === 'scenario' ? 'السيناريو' : 
                       name === 'visual' ? 'البصري' : 
                       name === 'audio' ? 'الصوتي' : 'المونتاج'}
                    </span>
                  </div>
                ))}
              </div>
              <Button variant="outline" size="sm" onClick={checkServicesStatus}>
                <RefreshCw className="h-4 w-4" />
              </Button>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="container mx-auto px-6 py-8">
        <Tabs defaultValue="dashboard" className="w-full">
          <TabsList className="grid w-full grid-cols-6 mb-8">
            <TabsTrigger value="dashboard" className="flex items-center space-x-2 space-x-reverse">
              <Monitor className="h-4 w-4" />
              <span>لوحة التحكم</span>
            </TabsTrigger>
            <TabsTrigger value="scenario" className="flex items-center space-x-2 space-x-reverse">
              <FileText className="h-4 w-4" />
              <span>السيناريو</span>
            </TabsTrigger>
            <TabsTrigger value="visual" className="flex items-center space-x-2 space-x-reverse">
              <Image className="h-4 w-4" />
              <span>المحتوى البصري</span>
            </TabsTrigger>
            <TabsTrigger value="audio" className="flex items-center space-x-2 space-x-reverse">
              <Music className="h-4 w-4" />
              <span>المحتوى الصوتي</span>
            </TabsTrigger>
            <TabsTrigger value="editor" className="flex items-center space-x-2 space-x-reverse">
              <Edit3 className="h-4 w-4" />
              <span>المونتاج</span>
            </TabsTrigger>
            <TabsTrigger value="workflow" className="flex items-center space-x-2 space-x-reverse">
              <Zap className="h-4 w-4" />
              <span>سير العمل</span>
            </TabsTrigger>
          </TabsList>

          {/* Dashboard Tab */}
          <TabsContent value="dashboard" className="space-y-6">
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
              {/* Service Cards */}
              <Card className="hover:shadow-lg transition-shadow">
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                  <CardTitle className="text-sm font-medium">خدمة السيناريو</CardTitle>
                  <FileText className="h-4 w-4 text-muted-foreground" />
                </CardHeader>
                <CardContent>
                  <div className="flex items-center space-x-2 space-x-reverse">
                    <div className={`w-3 h-3 rounded-full ${getServiceStatusColor(services.scenario.status)}`}></div>
                    <span className="text-sm">{getServiceStatusText(services.scenario.status)}</span>
                  </div>
                  <p className="text-xs text-muted-foreground mt-2">
                    توليد السيناريوهات والقصص
                  </p>
                  <Button 
                    size="sm" 
                    className="w-full mt-3"
                    onClick={() => window.open(services.scenario.url, '_blank')}
                  >
                    فتح الخدمة
                  </Button>
                </CardContent>
              </Card>

              <Card className="hover:shadow-lg transition-shadow">
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                  <CardTitle className="text-sm font-medium">المحتوى البصري</CardTitle>
                  <Image className="h-4 w-4 text-muted-foreground" />
                </CardHeader>
                <CardContent>
                  <div className="flex items-center space-x-2 space-x-reverse">
                    <div className={`w-3 h-3 rounded-full ${getServiceStatusColor(services.visual.status)}`}></div>
                    <span className="text-sm">{getServiceStatusText(services.visual.status)}</span>
                  </div>
                  <p className="text-xs text-muted-foreground mt-2">
                    توليد الصور والمؤثرات البصرية
                  </p>
                  <Button 
                    size="sm" 
                    className="w-full mt-3"
                    onClick={() => window.open(services.visual.url, '_blank')}
                  >
                    فتح الخدمة
                  </Button>
                </CardContent>
              </Card>

              <Card className="hover:shadow-lg transition-shadow">
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                  <CardTitle className="text-sm font-medium">المحتوى الصوتي</CardTitle>
                  <Music className="h-4 w-4 text-muted-foreground" />
                </CardHeader>
                <CardContent>
                  <div className="flex items-center space-x-2 space-x-reverse">
                    <div className={`w-3 h-3 rounded-full ${getServiceStatusColor(services.audio.status)}`}></div>
                    <span className="text-sm">{getServiceStatusText(services.audio.status)}</span>
                  </div>
                  <p className="text-xs text-muted-foreground mt-2">
                    توليد الأصوات والموسيقى
                  </p>
                  <Button 
                    size="sm" 
                    className="w-full mt-3"
                    onClick={() => window.open(services.audio.url, '_blank')}
                  >
                    فتح الخدمة
                  </Button>
                </CardContent>
              </Card>

              <Card className="hover:shadow-lg transition-shadow">
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                  <CardTitle className="text-sm font-medium">المونتاج والتجميع</CardTitle>
                  <Edit3 className="h-4 w-4 text-muted-foreground" />
                </CardHeader>
                <CardContent>
                  <div className="flex items-center space-x-2 space-x-reverse">
                    <div className={`w-3 h-3 rounded-full ${getServiceStatusColor(services.editor.status)}`}></div>
                    <span className="text-sm">{getServiceStatusText(services.editor.status)}</span>
                  </div>
                  <p className="text-xs text-muted-foreground mt-2">
                    تجميع وتصدير الأفلام
                  </p>
                  <Button 
                    size="sm" 
                    className="w-full mt-3"
                    onClick={() => window.open(services.editor.url, '_blank')}
                  >
                    فتح الخدمة
                  </Button>
                </CardContent>
              </Card>
            </div>

            {/* Quick Actions */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center space-x-2 space-x-reverse">
                  <Sparkles className="h-5 w-5" />
                  <span>إجراءات سريعة</span>
                </CardTitle>
                <CardDescription>
                  ابدأ مشروع فيلم جديد أو تابع العمل على مشروع موجود
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  <Button className="h-20 flex flex-col items-center justify-center space-y-2">
                    <Film className="h-6 w-6" />
                    <span>مشروع جديد</span>
                  </Button>
                  <Button variant="outline" className="h-20 flex flex-col items-center justify-center space-y-2">
                    <Upload className="h-6 w-6" />
                    <span>استيراد مشروع</span>
                  </Button>
                  <Button variant="outline" className="h-20 flex flex-col items-center justify-center space-y-2">
                    <Settings className="h-6 w-6" />
                    <span>الإعدادات</span>
                  </Button>
                </div>
              </CardContent>
            </Card>

            {/* Recent Projects */}
            <Card>
              <CardHeader>
                <CardTitle>المشاريع الأخيرة</CardTitle>
                <CardDescription>
                  مشاريع الأفلام التي تم العمل عليها مؤخراً
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {projects.length === 0 ? (
                    <div className="text-center py-8 text-muted-foreground">
                      <Film className="h-12 w-12 mx-auto mb-4 opacity-50" />
                      <p>لا توجد مشاريع بعد</p>
                      <p className="text-sm">ابدأ مشروع جديد لرؤيته هنا</p>
                    </div>
                  ) : (
                    projects.map((project) => (
                      <div key={project.id} className="flex items-center justify-between p-4 border rounded-lg hover:bg-muted/50 transition-colors">
                        <div className="flex items-center space-x-4 space-x-reverse">
                          <div className="bg-primary/10 p-2 rounded-lg">
                            <Film className="h-5 w-5 text-primary" />
                          </div>
                          <div>
                            <h4 className="font-medium">{project.title}</h4>
                            <p className="text-sm text-muted-foreground">{project.description}</p>
                          </div>
                        </div>
                        <div className="flex items-center space-x-2 space-x-reverse">
                          <Badge variant="secondary">{project.status}</Badge>
                          <Button size="sm" variant="outline">
                            فتح
                          </Button>
                        </div>
                      </div>
                    ))
                  )}
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          {/* Scenario Tab */}
          <TabsContent value="scenario" className="space-y-6">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center space-x-2 space-x-reverse">
                  <FileText className="h-5 w-5" />
                  <span>خدمة توليد السيناريو</span>
                </CardTitle>
                <CardDescription>
                  إنشاء سيناريوهات وقصص الأفلام باستخدام الذكاء الاصطناعي
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="text-center py-8">
                  <FileText className="h-16 w-16 mx-auto mb-4 text-muted-foreground" />
                  <h3 className="text-lg font-medium mb-2">خدمة السيناريو</h3>
                  <p className="text-muted-foreground mb-4">
                    انقر على الزر أدناه لفتح واجهة توليد السيناريو
                  </p>
                  <Button 
                    size="lg"
                    onClick={() => window.open(services.scenario.url, '_blank')}
                    disabled={services.scenario.status !== 'online'}
                  >
                    <FileText className="h-4 w-4 mr-2" />
                    فتح خدمة السيناريو
                  </Button>
                  {services.scenario.status !== 'online' && (
                    <p className="text-sm text-red-500 mt-2">
                      الخدمة غير متاحة حالياً
                    </p>
                  )}
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          {/* Visual Tab */}
          <TabsContent value="visual" className="space-y-6">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center space-x-2 space-x-reverse">
                  <Image className="h-5 w-5" />
                  <span>خدمة المحتوى البصري</span>
                </CardTitle>
                <CardDescription>
                  توليد الصور والمؤثرات البصرية للأفلام
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="text-center py-8">
                  <Image className="h-16 w-16 mx-auto mb-4 text-muted-foreground" />
                  <h3 className="text-lg font-medium mb-2">المحتوى البصري</h3>
                  <p className="text-muted-foreground mb-4">
                    انقر على الزر أدناه لفتح واجهة توليد المحتوى البصري
                  </p>
                  <Button 
                    size="lg"
                    onClick={() => window.open(services.visual.url, '_blank')}
                    disabled={services.visual.status !== 'online'}
                  >
                    <Image className="h-4 w-4 mr-2" />
                    فتح خدمة المحتوى البصري
                  </Button>
                  {services.visual.status !== 'online' && (
                    <p className="text-sm text-red-500 mt-2">
                      الخدمة غير متاحة حالياً
                    </p>
                  )}
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          {/* Audio Tab */}
          <TabsContent value="audio" className="space-y-6">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center space-x-2 space-x-reverse">
                  <Music className="h-5 w-5" />
                  <span>خدمة المحتوى الصوتي</span>
                </CardTitle>
                <CardDescription>
                  توليد الأصوات والموسيقى والمؤثرات الصوتية
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="text-center py-8">
                  <Music className="h-16 w-16 mx-auto mb-4 text-muted-foreground" />
                  <h3 className="text-lg font-medium mb-2">المحتوى الصوتي</h3>
                  <p className="text-muted-foreground mb-4">
                    انقر على الزر أدناه لفتح واجهة توليد المحتوى الصوتي
                  </p>
                  <Button 
                    size="lg"
                    onClick={() => window.open(services.audio.url, '_blank')}
                    disabled={services.audio.status !== 'online'}
                  >
                    <Music className="h-4 w-4 mr-2" />
                    فتح خدمة المحتوى الصوتي
                  </Button>
                  {services.audio.status !== 'online' && (
                    <p className="text-sm text-red-500 mt-2">
                      الخدمة غير متاحة حالياً
                    </p>
                  )}
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          {/* Editor Tab */}
          <TabsContent value="editor" className="space-y-6">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center space-x-2 space-x-reverse">
                  <Edit3 className="h-5 w-5" />
                  <span>خدمة المونتاج والتجميع</span>
                </CardTitle>
                <CardDescription>
                  تجميع العناصر وتصدير الأفلام النهائية
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="text-center py-8">
                  <Edit3 className="h-16 w-16 mx-auto mb-4 text-muted-foreground" />
                  <h3 className="text-lg font-medium mb-2">المونتاج والتجميع</h3>
                  <p className="text-muted-foreground mb-4">
                    انقر على الزر أدناه لفتح واجهة المونتاج والتجميع
                  </p>
                  <Button 
                    size="lg"
                    onClick={() => window.open(services.editor.url, '_blank')}
                    disabled={services.editor.status !== 'online'}
                  >
                    <Edit3 className="h-4 w-4 mr-2" />
                    فتح خدمة المونتاج
                  </Button>
                  {services.editor.status !== 'online' && (
                    <p className="text-sm text-red-500 mt-2">
                      الخدمة غير متاحة حالياً
                    </p>
                  )}
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          {/* Workflow Tab */}
          <TabsContent value="workflow" className="space-y-6">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center space-x-2 space-x-reverse">
                  <Zap className="h-5 w-5" />
                  <span>سير العمل التلقائي</span>
                </CardTitle>
                <CardDescription>
                  إنشاء فيلم كامل بخطوات تلقائية متتالية
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-6">
                  {/* Workflow Steps */}
                  <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                    <div className="flex flex-col items-center p-4 border rounded-lg">
                      <div className="bg-blue-100 dark:bg-blue-900 p-3 rounded-full mb-3">
                        <FileText className="h-6 w-6 text-blue-600 dark:text-blue-400" />
                      </div>
                      <h4 className="font-medium mb-2">1. السيناريو</h4>
                      <p className="text-sm text-muted-foreground text-center">
                        توليد السيناريو والشخصيات
                      </p>
                    </div>

                    <div className="flex flex-col items-center p-4 border rounded-lg">
                      <div className="bg-green-100 dark:bg-green-900 p-3 rounded-full mb-3">
                        <Image className="h-6 w-6 text-green-600 dark:text-green-400" />
                      </div>
                      <h4 className="font-medium mb-2">2. المحتوى البصري</h4>
                      <p className="text-sm text-muted-foreground text-center">
                        إنشاء الصور والمشاهد
                      </p>
                    </div>

                    <div className="flex flex-col items-center p-4 border rounded-lg">
                      <div className="bg-purple-100 dark:bg-purple-900 p-3 rounded-full mb-3">
                        <Music className="h-6 w-6 text-purple-600 dark:text-purple-400" />
                      </div>
                      <h4 className="font-medium mb-2">3. المحتوى الصوتي</h4>
                      <p className="text-sm text-muted-foreground text-center">
                        توليد الأصوات والموسيقى
                      </p>
                    </div>

                    <div className="flex flex-col items-center p-4 border rounded-lg">
                      <div className="bg-orange-100 dark:bg-orange-900 p-3 rounded-full mb-3">
                        <Video className="h-6 w-6 text-orange-600 dark:text-orange-400" />
                      </div>
                      <h4 className="font-medium mb-2">4. المونتاج</h4>
                      <p className="text-sm text-muted-foreground text-center">
                        تجميع وتصدير الفيلم
                      </p>
                    </div>
                  </div>

                  {/* Workflow Form */}
                  <div className="border rounded-lg p-6">
                    <h4 className="font-medium mb-4">إنشاء فيلم تلقائي</h4>
                    <div className="space-y-4">
                      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                        <div>
                          <Label htmlFor="movieTitle">عنوان الفيلم</Label>
                          <Input id="movieTitle" placeholder="اكتب عنوان الفيلم..." />
                        </div>
                        <div>
                          <Label htmlFor="movieGenre">النوع</Label>
                          <Select>
                            <SelectTrigger>
                              <SelectValue placeholder="اختر نوع الفيلم" />
                            </SelectTrigger>
                            <SelectContent>
                              <SelectItem value="drama">دراما</SelectItem>
                              <SelectItem value="comedy">كوميديا</SelectItem>
                              <SelectItem value="action">أكشن</SelectItem>
                              <SelectItem value="sci-fi">خيال علمي</SelectItem>
                              <SelectItem value="documentary">وثائقي</SelectItem>
                            </SelectContent>
                          </Select>
                        </div>
                      </div>
                      <div>
                        <Label htmlFor="movieIdea">الفكرة الأساسية</Label>
                        <Textarea 
                          id="movieIdea" 
                          placeholder="اكتب فكرة الفيلم الأساسية..." 
                          className="min-h-[100px]"
                        />
                      </div>
                      <Button size="lg" className="w-full">
                        <Zap className="h-4 w-4 mr-2" />
                        بدء إنتاج الفيلم التلقائي
                      </Button>
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>
      </main>
    </div>
  )
}

export default App

