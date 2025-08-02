#!/bin/bash

# AI Movie Agent - Service Startup Script
# وكيل الذكاء الاصطناعي لإنتاج الأفلام - سكريبت تشغيل الخدمات

echo "🎬 Starting AI Movie Agent Services..."
echo "======================================"

# Function to check if a port is available
check_port() {
    local port=$1
    if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null ; then
        echo "⚠️  Port $port is already in use"
        return 1
    else
        echo "✅ Port $port is available"
        return 0
    fi
}

# Function to start a service
start_service() {
    local service_name=$1
    local service_dir=$2
    local port=$3
    
    echo ""
    echo "🚀 Starting $service_name on port $port..."
    
    if ! check_port $port; then
        echo "❌ Cannot start $service_name - port $port is busy"
        return 1
    fi
    
    cd $service_dir
    
    # Activate virtual environment if it exists
    if [ -d "venv" ]; then
        echo "   Activating virtual environment..."
        source venv/bin/activate
    fi
    
    # Start the service in background
    if [ "$service_name" = "AI Movie Studio (Frontend)" ]; then
        npm run dev -- --host > ../logs/${service_name,,}.log 2>&1 &
    else
        python src/main.py > ../logs/${service_name,,}.log 2>&1 &
    fi
    
    local pid=$!
    echo "   Started with PID: $pid"
    echo $pid > ../pids/${service_name,,}.pid
    
    cd ..
    return 0
}

# Create directories for logs and PIDs
mkdir -p logs pids

# Clear old logs
rm -f logs/*.log
rm -f pids/*.pid

echo ""
echo "📋 Checking system requirements..."

# Check Python
if ! command -v python &> /dev/null; then
    echo "❌ Python is not installed"
    exit 1
else
    echo "✅ Python: $(python --version)"
fi

# Check Node.js
if ! command -v node &> /dev/null; then
    echo "❌ Node.js is not installed"
    exit 1
else
    echo "✅ Node.js: $(node --version)"
fi

# Check npm
if ! command -v npm &> /dev/null; then
    echo "❌ npm is not installed"
    exit 1
else
    echo "✅ npm: $(npm --version)"
fi

echo ""
echo "🔧 Setting up virtual environments..."

# Setup Python virtual environments
for service in scenario_generator visual_generator audio_generator movie_editor; do
    if [ ! -d "$service/venv" ]; then
        echo "   Creating virtual environment for $service..."
        cd $service
        python -m venv venv
        source venv/bin/activate
        pip install --upgrade pip
        if [ -f "requirements.txt" ]; then
            pip install -r requirements.txt
        fi
        deactivate
        cd ..
    else
        echo "   Virtual environment for $service already exists"
    fi
done

# Setup Node.js dependencies
if [ ! -d "ai-movie-studio/node_modules" ]; then
    echo "   Installing Node.js dependencies for frontend..."
    cd ai-movie-studio
    npm install
    cd ..
else
    echo "   Node.js dependencies for frontend already installed"
fi

echo ""
echo "🎯 Starting services..."

# Start backend services
start_service "Scenario Generator" "scenario_generator" 5000
sleep 2

start_service "Visual Generator" "visual_generator" 5001
sleep 2

start_service "Audio Generator" "audio_generator" 5002
sleep 2

start_service "Movie Editor" "movie_editor" 5003
sleep 2

# Start frontend
start_service "AI Movie Studio (Frontend)" "ai-movie-studio" 5173

echo ""
echo "⏳ Waiting for services to initialize..."
sleep 5

echo ""
echo "🎉 All services started successfully!"
echo "=================================="
echo ""
echo "🌐 Access URLs:"
echo "   • Main Interface:     http://localhost:5173"
echo "   • Scenario Generator: http://localhost:5000"
echo "   • Visual Generator:   http://localhost:5001"
echo "   • Audio Generator:    http://localhost:5002"
echo "   • Movie Editor:       http://localhost:5003"
echo ""
echo "📊 Service Status:"

# Check service status
for port in 5000 5001 5002 5003 5173; do
    if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null ; then
        echo "   ✅ Port $port: Running"
    else
        echo "   ❌ Port $port: Not running"
    fi
done

echo ""
echo "📝 Logs are available in the 'logs' directory"
echo "🔧 PIDs are stored in the 'pids' directory"
echo ""
echo "To stop all services, run: ./stop_services.sh"
echo ""
echo "🎬 Happy movie making! 🎭"

