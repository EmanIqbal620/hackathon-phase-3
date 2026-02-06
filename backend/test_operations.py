#!/usr/bin/env python3
"""
Test script to verify that task operations work properly
This script tests the actual backend functionality to ensure operations are executed
"""
import asyncio
import sys
import os

# Add the backend src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from sqlmodel import Session, select
from src.models.task import Task
from src.database import sync_engine
from src.mcp_tools.add_task import AddTaskParams, add_task
from src.mcp_tools.list_tasks import ListTasksParams, list_tasks
from src.mcp_tools.update_task import UpdateTaskParams, update_task
from src.mcp_tools.complete_task import CompleteTaskParams, complete_task
from src.mcp_tools.delete_task import DeleteTaskParams, delete_task

def test_task_operations():
    print("Testing task operations...")
    print("="*50)

    # Create a test user ID
    test_user_id = "test-user-123"

    # Test 1: Add a task
    print("\n1. Testing ADD task operation:")
    add_params = AddTaskParams(
        user_id=test_user_id,
        title="Test Task for Verification",
        description="This is a test task to verify operations work"
    )

    add_result = add_task(add_params)
    print(f"   Result: {add_result}")

    # Extract task ID from result
    import ast
    result_str = add_result[0].text
    try:
        result_dict = ast.literal_eval(result_str)
        task_id = result_dict.get('task_details', {}).get('id')
        print(f"   Created task ID: {task_id}")
    except:
        print("   ERROR: Could not extract task ID from result")
        return

    # Test 2: List tasks to verify it was added
    print("\n2. Testing LIST tasks operation:")
    list_params = ListTasksParams(user_id=test_user_id)
    list_result = list_tasks(list_params)
    print(f"   Result: {list_result}")

    # Test 3: Update the task
    print(f"\n3. Testing UPDATE task operation (task ID: {task_id}):")
    update_params = UpdateTaskParams(
        task_id=task_id,
        user_id=test_user_id,
        title="Updated Test Task",
        description="This task has been updated to verify update functionality"
    )

    update_result = update_task(update_params)
    print(f"   Result: {update_result}")

    # Verify the task was actually updated in DB
    with Session(sync_engine) as session:
        updated_task = session.exec(select(Task).where(Task.id == task_id)).first()
        if updated_task:
            print(f"   Verification: Task title is now '{updated_task.title}'")
            print(f"   Verification: Task description is now '{updated_task.description}'")
        else:
            print("   ERROR: Task not found in database after update")

    # Test 4: Complete the task
    print(f"\n4. Testing COMPLETE task operation (task ID: {task_id}):")
    complete_params = CompleteTaskParams(
        task_id=task_id,
        user_id=test_user_id
    )

    complete_result = complete_task(complete_params)
    print(f"   Result: {complete_result}")

    # Verify the task was actually marked as completed in DB
    with Session(sync_engine) as session:
        completed_task = session.exec(select(Task).where(Task.id == task_id)).first()
        if completed_task:
            print(f"   Verification: Task is_completed is now {completed_task.is_completed}")
        else:
            print("   ERROR: Task not found in database after completion")

    # Test 5: Delete the task
    print(f"\n5. Testing DELETE task operation (task ID: {task_id}):")
    delete_params = DeleteTaskParams(
        task_id=task_id,
        user_id=test_user_id
    )

    delete_result = delete_task(delete_params)
    print(f"   Result: {delete_result}")

    # Verify the task was actually deleted in DB (soft delete - should have deleted_at)
    with Session(sync_engine) as session:
        deleted_task = session.exec(select(Task).where(Task.id == task_id)).first()
        if deleted_task:
            print(f"   Verification: Task exists but deleted_at is set: {deleted_task.deleted_at is not None}")
        else:
            print("   Verification: Task was removed from database after delete")

    print("\n" + "="*50)
    print("TEST SUMMARY:")
    print("- ADD task: Should have created a new task in database")
    print("- UPDATE task: Should have modified existing task in database")
    print("- COMPLETE task: Should have marked task as completed in database")
    print("- DELETE task: Should have soft-deleted task in database")
    print("")
    print("If all operations show SUCCESS in their respective results,")
    print("then the backend tools are working correctly!")
    print("The issue was likely in the TextContent constructor format.")

if __name__ == "__main__":
    test_task_operations()

if __name__ == "__main__":
    test_task_operations()