#!/usr/bin/env python3
"""
Comprehensive test script to verify all chatbot functionalities.
"""

import requests
import json
import time

def test_comprehensive():
    base_url = "http://127.0.0.1:8000"

    print("Comprehensive chatbot functionality test...")

    try:
        # Register a new test user
        test_email = f"test_comp_{int(time.time())}@example.com"
        register_data = {
            "name": "Comprehensive Test User",
            "email": test_email,
            "password": "testpassword123"
        }

        print(f"Registering test user: {test_email}")

        # Register the test user
        register_resp = requests.post(f"{base_url}/api/auth/register", json=register_data)
        print(f"Registration response: {register_resp.status_code}")

        if register_resp.status_code in [200, 201]:
            auth_data = register_resp.json()
            user_id = auth_data.get('user_id', 'unknown')

            # Login to get the token
            login_data = {
                "email": test_email,
                "password": "testpassword123"
            }

            login_resp = requests.post(f"{base_url}/api/auth/login", json=login_data)
            if login_resp.status_code == 200:
                login_response = login_resp.json()
                token = login_response.get('access_token', '')

                print(f"Logged in as user: {user_id}")

                headers = {
                    'Authorization': f'Bearer {token}',
                    'Content-Type': 'application/json'
                }

                # Test all functionality
                test_functions = [
                    ("Add Task", "add a task to study mathematics", "add_task"),
                    ("Show Tasks", "show my tasks", "list_tasks"),
                    ("Update Task", "update task study to study physics", "update_task"),
                    ("Complete Task", "mark first task as complete", "complete_task"),
                    ("Delete Task", "delete first task", "delete_task")
                ]

                for func_name, command, expected_tool in test_functions:
                    print(f"\n--- Testing {func_name}: {command} ---")

                    payload = {
                        "conversation_id": None,
                        "message": command
                    }

                    resp = requests.post(
                        f"{base_url}/api/chat/{user_id}",
                        json=payload,
                        headers=headers
                    )

                    print(f"Status: {resp.status_code}")

                    if resp.status_code == 200:
                        response_data = resp.json()
                        response_text = response_data.get('response', 'No response')
                        safe_response = response_text.encode('ascii', 'ignore').decode('ascii')
                        print(f"AI Response: {safe_response}")

                        if response_data.get('tool_calls'):
                            print(f"Tool Calls: {len(response_data['tool_calls'])} executed")
                            for tool_call in response_data['tool_calls']:
                                tool_name = tool_call.get('tool', 'unknown')
                                status = tool_call.get('status', 'unknown')
                                safe_tool_name = tool_name.encode('ascii', 'ignore').decode('ascii')
                                safe_status = status.encode('ascii', 'ignore').decode('ascii')
                                print(f"  - Tool: {safe_tool_name}, Status: {safe_status}")

                                if tool_name == expected_tool:
                                    print(f"  ✓ Expected tool {expected_tool} was called!")
                                else:
                                    print(f"  ⚠ Expected {expected_tool}, got {safe_tool_name}")
                        else:
                            print("  ⚠ No tool calls executed")
                    else:
                        error_text = resp.text.encode('ascii', 'ignore').decode('ascii')
                        print(f"Error: {error_text}")

                    time.sleep(1)
            else:
                print(f"Login failed: {login_resp.status_code}, {login_resp.text}")
        else:
            print(f"Registration failed: {register_resp.status_code}, {register_resp.text}")

    except requests.exceptions.ConnectionError:
        print("Could not connect to server. Is the backend running on http://127.0.0.1:8000?")
    except Exception as e:
        print(f"Error during testing: {e}")

if __name__ == "__main__":
    test_comprehensive()