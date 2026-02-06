#!/bin/bash

echo "Building Todo App Docker containers..."

echo ""
echo "Building backend container..."
cd backend
docker build -t todo-backend .
if [ $? -ne 0 ]; then
    echo "Failed to build backend container"
    exit 1
fi
cd ..

echo ""
echo "Building frontend container..."
cd frontend
docker build -t todo-frontend .
if [ $? -ne 0 ]; then
    echo "Failed to build frontend container"
    exit 1
fi
cd ..

echo ""
echo "All containers built successfully!"

echo ""
echo "To run individual containers, use the commands in the README."