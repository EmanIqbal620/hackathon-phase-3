@echo off
setlocal

echo Starting Todo App containers...

echo.
echo To run the containers individually, use the commands in the README.
echo Example:
echo docker run -d -p 5432:5432 --name todo-db postgres:15
echo docker run -d -p 7860:7860 --name todo-backend --link todo-db -e DATABASE_URL=postgresql://postgres:password@todo-db:5432/todoapp todo-backend
echo docker run -d -p 3000:7860 --name todo-frontend --link todo-backend -e NEXT_PUBLIC_API_URL=http://localhost:7860 todo-frontend