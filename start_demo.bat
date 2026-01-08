@echo off
echo 🚀 Starting Project Synapse Demo
echo ================================

echo 📦 Installing frontend dependencies...
cd frontend
call npm install

if %errorlevel% neq 0 (
    echo ❌ Failed to install dependencies
    pause
    exit /b 1
)

echo 🌐 Starting frontend development server...
echo.
echo 📖 The frontend will be available at: http://localhost:3000
echo 📖 Note: Backend API is not running (would be at http://localhost:8080)
echo 📖 The frontend will show demo data and mock interactions
echo.
echo 🛑 Press Ctrl+C to stop the server
echo.

call npm start