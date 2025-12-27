#!/bin/bash

BASE_DIR=$(pwd)
LOG_DIR="$BASE_DIR/logs"

echo "Stopping Application..."

# Stop Backend
if [ -f "$LOG_DIR/backend.pid" ]; then
    BACKEND_PID=$(cat "$LOG_DIR/backend.pid")
    if ps -p $BACKEND_PID > /dev/null; then
        echo "Stopping Backend (PID: $BACKEND_PID)..."
        kill $BACKEND_PID
    else
        echo "Backend process $BACKEND_PID not found."
    fi
    rm "$LOG_DIR/backend.pid"
else
    echo "Backend PID file not found."
fi

# Stop Frontend
if [ -f "$LOG_DIR/frontend.pid" ]; then
    FRONTEND_PID=$(cat "$LOG_DIR/frontend.pid")
    # Process group kill might be needed for npm -> vite, but simple kill often works for top level
    # If npm spawns children, we might need kill -- -$PGID or pkill -P
    if ps -p $FRONTEND_PID > /dev/null; then
        echo "Stopping Frontend (PID: $FRONTEND_PID)..."
        kill $FRONTEND_PID
    else
        echo "Frontend process $FRONTEND_PID not found."
    fi
    rm "$LOG_DIR/frontend.pid"
else
    echo "Frontend PID file not found."
fi

echo "Application stopped."
