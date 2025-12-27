#!/bin/bash

# Define paths
BASE_DIR=$(pwd)
LOG_DIR="$BASE_DIR/logs"

# Create logs directory if it doesn't exist
mkdir -p "$LOG_DIR"

echo "Starting Application..."

# Start Backend
echo "Starting Backend..."
cd "$BASE_DIR/backend"
# Use uv to run uvicorn
# Nohup to keep running after shell closes, save PID
nohup uv run uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload > "$LOG_DIR/backend.log" 2>&1 &
BACKEND_PID=$!
echo $BACKEND_PID > "$LOG_DIR/backend.pid"
echo "Backend started with PID $BACKEND_PID. Logs: $LOG_DIR/backend.log"

# Start Frontend
echo "Starting Frontend..."
cd "$BASE_DIR/frontend"
# Nohup for frontend dev server
nohup npm run dev > "$LOG_DIR/frontend.log" 2>&1 &
FRONTEND_PID=$!
echo $FRONTEND_PID > "$LOG_DIR/frontend.pid"
echo "Frontend started with PID $FRONTEND_PID. Logs: $LOG_DIR/frontend.log"

echo "Application started successfully."
echo "Backend: http://localhost:8000"
echo "Frontend: http://localhost:5173"
