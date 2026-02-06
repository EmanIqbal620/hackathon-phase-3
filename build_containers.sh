#!/bin/bash

echo "Building Todo App Containers..."

echo ""
echo "Building Backend Container..."
cd backend
docker build -f Dockerfile.backend -t todo-backend .

echo ""
echo "Building Frontend Container..."
cd ../frontend
docker build -f Dockerfile.frontend -t todo-frontend .

echo ""
echo "Build Complete!"
echo ""
echo "To run the containers separately:"
echo ""
echo "1. Start database: docker run --name todo-db -e POSTGRES_DB=todoapp -e POSTGRES_USER=postgres -e POSTGRES_PASSWORD=password -p 5432:5432 -d postgres:15"
echo ""
echo "2. Start backend: docker run --name todo-backend --link todo-db -e DATABASE_URL=postgresql://postgres:password@todo-db:5432/todoapp -p 8000:8000 -d todo-backend"
echo ""
echo "3. Start frontend: docker run --name todo-frontend --link todo-backend -e NEXT_PUBLIC_API_URL=http://localhost:8000 -p 3000:80 -d todo-frontend"