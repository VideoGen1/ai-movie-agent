#!/bin/bash

# AI Movie Agent - Service Stop Script
# وكيل الذكاء الاصطناعي لإنتاج الأفلام - سكريبت إيقاف الخدمات

echo "🛑 Stopping AI Movie Agent Services..."
echo "====================================="

# Function to stop a service by PID file
stop_service_by_pid() {
    local service_name=$1
    local pid_file="pids/${service_name,,}.pid"
    
    if [ -f "$pid_file" ]; then
        local pid=$(cat "$pid_file")
        if ps -p $pid > /dev/null 2>&1; then
            echo "🔄 Stopping $service_name (PID: $pid)..."
            kill $pid
            
            # Wait for graceful shutdown
            sleep 2
            
            # Force kill if still running
            if ps -p $pid > /dev/null 2>&1; then
                echo "   Force killing $service_name..."
                kill -9 $pid
            fi
            
            echo "   ✅ $service_name stopped"
        else
            echo "   ⚠️  $service_name was not running"
        fi
        rm -f "$pid_file"
    else
        echo "   ⚠️  No PID file found for $service_name"
    fi
}

# Function to stop services by port
stop_service_by_port() {
    local port=$1
    local service_name=$2
    
    local pid=$(lsof -ti:$port)
    if [ ! -z "$pid" ]; then
        echo "🔄 Stopping $service_name on port $port (PID: $pid)..."
        kill $pid
        sleep 2
        
        # Force kill if still running
        local check_pid=$(lsof -ti:$port)
        if [ ! -z "$check_pid" ]; then
            echo "   Force killing process on port $port..."
            kill -9 $check_pid
        fi
        
        echo "   ✅ $service_name stopped"
    else
        echo "   ⚠️  No process running on port $port"
    fi
}

echo ""
echo "🔍 Checking running services..."

# Check which services are running
for port in 5000 5001 5002 5003 5173; do
    if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null ; then
        echo "   🟢 Port $port: Running"
    else
        echo "   🔴 Port $port: Not running"
    fi
done

echo ""
echo "🛑 Stopping services..."

# Stop services by PID files first
if [ -d "pids" ]; then
    stop_service_by_pid "Scenario Generator"
    stop_service_by_pid "Visual Generator"
    stop_service_by_pid "Audio Generator"
    stop_service_by_pid "Movie Editor"
    stop_service_by_pid "AI Movie Studio (Frontend)"
fi

# Stop any remaining processes by port
stop_service_by_port 5000 "Scenario Generator"
stop_service_by_port 5001 "Visual Generator"
stop_service_by_port 5002 "Audio Generator"
stop_service_by_port 5003 "Movie Editor"
stop_service_by_port 5173 "AI Movie Studio"

# Clean up any Python processes that might be related
echo ""
echo "🧹 Cleaning up related processes..."

# Kill any remaining Flask processes
pkill -f "python src/main.py" 2>/dev/null && echo "   ✅ Stopped remaining Python services"

# Kill any remaining npm/node processes for our project
pkill -f "npm run dev" 2>/dev/null && echo "   ✅ Stopped remaining npm processes"
pkill -f "vite.*--host" 2>/dev/null && echo "   ✅ Stopped remaining Vite processes"

echo ""
echo "🔍 Final status check..."

# Final check
all_stopped=true
for port in 5000 5001 5002 5003 5173; do
    if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null ; then
        echo "   ❌ Port $port: Still running"
        all_stopped=false
    else
        echo "   ✅ Port $port: Stopped"
    fi
done

# Clean up directories
echo ""
echo "🧹 Cleaning up temporary files..."

if [ -d "pids" ]; then
    rm -f pids/*.pid
    echo "   ✅ Cleaned PID files"
fi

if [ -d "logs" ]; then
    # Keep logs but compress old ones
    find logs -name "*.log" -mtime +7 -exec gzip {} \;
    echo "   ✅ Cleaned old log files"
fi

echo ""
if [ "$all_stopped" = true ]; then
    echo "🎉 All services stopped successfully!"
    echo "================================="
else
    echo "⚠️  Some services may still be running"
    echo "======================================"
    echo "You may need to manually kill remaining processes"
fi

echo ""
echo "📊 System resources freed up"
echo "🔄 Ready to restart with: ./start_services.sh"
echo ""
echo "👋 Goodbye!"

