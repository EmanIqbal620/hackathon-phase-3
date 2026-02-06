#!/usr/bin/env python3
"""Test script to see what happens when creating a Task with minimal fields"""

from src.models.task import Task

def test_task_creation():
    print("Testing Task creation with minimal fields...")

    try:
        # This mimics what TaskService.create_task does
        task = Task(
            title="Test Task",
            description="This is a test task",
            user_id="some-user-id"
        )
        print(f"Task created successfully: {task.title}, priority: {task.priority}")
        print(f"All fields: {task.__dict__.keys()}")
    except Exception as e:
        print(f"Error creating task: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_task_creation()