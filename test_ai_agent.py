"""
Test script to verify the AI Agent functionality
"""

import requests
import json

# Configuration
BASE_URL = "http://localhost:8000"  # Replace with your actual backend URL
TEST_TOKEN = "your-test-jwt-token-here"  # Replace with a valid JWT token

def test_ai_agent():
    """Test the AI agent endpoint with various task operations"""

    headers = {
        "Authorization": f"Bearer {TEST_TOKEN}",
        "Content-Type": "application/json"
    }

    # Test 1: Add a task
    print("Testing: Add task")
    add_task_message = {
        "user_id": "test-user-123",
        "conversation_id": None,
        "message": "Add a task to buy groceries",
        "timestamp": "2023-12-07T10:30:00Z"
    }

    response = requests.post(f"{BASE_URL}/api/ai-agent/message",
                           json=add_task_message, headers=headers)
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}\n")

    # Test 2: List tasks
    print("Testing: List tasks")
    list_tasks_message = {
        "user_id": "test-user-123",
        "conversation_id": None,
        "message": "Show me my tasks",
        "timestamp": "2023-12-07T10:31:00Z"
    }

    response = requests.post(f"{BASE_URL}/api/ai-agent/message",
                           json=list_tasks_message, headers=headers)
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}\n")

    # Test 3: Update a task (assuming task ID 1 exists)
    print("Testing: Update task")
    update_task_message = {
        "user_id": "test-user-123",
        "conversation_id": None,
        "message": "Mark task 1 as completed",
        "timestamp": "2023-12-07T10:32:00Z"
    }

    response = requests.post(f"{BASE_URL}/api/ai-agent/message",
                           json=update_task_message, headers=headers)
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}\n")

def test_intent_detection():
    """Test the intent detection logic directly"""
    test_messages = [
        "Add a task to buy groceries",
        "Delete task 1",
        "Update task 2 to mark as done",
        "Show me my tasks",
        "Tell me a joke"
    ]

    for message in test_messages:
        print(f"Message: '{message}'")
        # This would require calling the backend directly or having a test endpoint
        # For now, this is just illustrative
        print("  -> Would be processed by AI agent intent detection\n")

if __name__ == "__main__":
    print("Testing AI Agent functionality...\n")

    # Run intent detection tests
    test_intent_detection()

    # Note: To run the full API tests, you need:
    # 1. A running backend server
    # 2. A valid JWT token
    # Uncomment the next line when ready to test:
    # test_ai_agent()

    print("\nTest script completed. Remember to:")
    print("1. Start your backend server")
    print("2. Obtain a valid JWT token")
    print("3. Update the BASE_URL and TEST_TOKEN variables")
    print("4. Uncomment test_ai_agent() call to run full API tests")