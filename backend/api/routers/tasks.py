from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import select, Session, desc
from typing import List
from datetime import datetime

from src.models import Task, TaskCreate, TaskRead, TaskUpdate
from dependencies import get_current_user
from database import sync_engine

router = APIRouter()

@router.get("/tasks", response_model=List[TaskRead])
def list_tasks(current_user=Depends(get_current_user)):
    with Session(sync_engine) as session:
        statement = select(Task).where(Task.user_id == current_user.id).order_by(desc(Task.created_at))
        tasks = session.exec(statement).all()
        return tasks

@router.post("/tasks", response_model=TaskRead, status_code=status.HTTP_201_CREATED)
def create_task(task: TaskCreate, current_user=Depends(get_current_user)):
    with Session(sync_engine) as session:
        db_task = Task.model_validate(task)
        db_task.user_id = current_user.id
        session.add(db_task)
        session.commit()
        session.refresh(db_task)
        return db_task

@router.get("/tasks/{task_id}", response_model=TaskRead)
def get_task(task_id: int, current_user=Depends(get_current_user)):
    with Session(sync_engine) as session:
        statement = select(Task).where(Task.id == task_id, Task.user_id == current_user.id)
        task = session.exec(statement).first()
        if not task:
            raise HTTPException(status_code=404, detail="Task not found")
        return task

@router.put("/tasks/{task_id}", response_model=TaskRead)
def update_task(task_id: int, task_update: TaskUpdate, current_user=Depends(get_current_user)):
    with Session(sync_engine) as session:
        statement = select(Task).where(Task.id == task_id, Task.user_id == current_user.id)
        db_task = session.exec(statement).first()
        if not db_task:
            raise HTTPException(status_code=404, detail="Task not found")

        # Update fields
        task_data = task_update.model_dump(exclude_unset=True)
        for field, value in task_data.items():
            setattr(db_task, field, value)

        db_task.updated_at = datetime.utcnow()
        session.add(db_task)
        session.commit()
        session.refresh(db_task)
        return db_task

@router.delete("/tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(task_id: int, current_user=Depends(get_current_user)):
    with Session(sync_engine) as session:
        statement = select(Task).where(Task.id == task_id, Task.user_id == current_user.id)
        db_task = session.exec(statement).first()
        if not db_task:
            raise HTTPException(status_code=404, detail="Task not found")

        session.delete(db_task)
        session.commit()
        return

@router.patch("/tasks/{task_id}/toggle", response_model=TaskRead)
def toggle_task_completion(task_id: int, current_user=Depends(get_current_user)):
    with Session(sync_engine) as session:
        statement = select(Task).where(Task.id == task_id, Task.user_id == current_user.id)
        db_task = session.exec(statement).first()
        if not db_task:
            raise HTTPException(status_code=404, detail="Task not found")

        db_task.completed = not db_task.completed
        db_task.updated_at = datetime.utcnow()
        session.add(db_task)
        session.commit()
        session.refresh(db_task)
        return db_task