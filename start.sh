#!/bin/bash

# Function to handle the termination signal (Ctrl+C)
function cleanup {
    echo "Stopping processes..."
    kill $BACKEND_PID
    kill $FRONTEND_PID
    exit
}

# Register the cleanup function to be called on Ctrl+C
trap cleanup INT

# Start the backend process
cd backend
source .venv/bin/activate
uvicorn app.main:app --ws-max-size 110000000 &
BACKEND_PID=$!

# Start the frontend process
cd ../client
npm run dev &
FRONTEND_PID=$!

# Wait for both processes to finish
wait $BACKEND_PID
wait $FRONTEND_PID