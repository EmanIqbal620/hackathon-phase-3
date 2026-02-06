#!/usr/bin/env python3
"""
Simple test script to verify update task functionality.
"""

import requests
import json
import time

def test_update_simple():
    base_url = "http://127.0.0.1:8000"

    print("Simple update task test...")

    try:
        # Register a new test user
        test_email = f"test_upd_{int(time.time())}@example.com"
        register_data = {
            "name": "Update Test User",
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

                # Step 1: Add a task first
                print(f"\nStep 1: Adding a task")
                add_payload = {
                    "conversation_id": None,
                    "message": "add a task to study mathematics"
                }

                add_resp = requests.post(
                    f"{base_url}/api/chat/{user_id}",
                    json=add_payload,
                    headers=headers
                )

                if add_resp.status_code == 200:
                    add_response_data = add_resp.json()
                    print(f"Add response: {add_response_data.get('response', 'No response')[:50]}...")

                    # Step 2: Update the task
                    print(f"\nStep 2: Updating the task")
                    update_payload = {
                        "conversation_id": None,
                        "message": "update task study to study physics"
                    }

                    update_resp = requests.post(
                        f"{base_url}/api/chat/{user_id}",
                        json=update_payload,
                        headers=headers
                    )

                    if update_resp.status_code == 200:
                        update_response_data = update_resp.json()
                        print(f"Update response: {update_response_data.get('response', 'No response')[:100]}...")

                        if update_response_data.get('tool_calls'):
                            for tool_call in update_response_data['tool_calls']:
                                tool_name = tool_call.get('tool', 'unknown')
                                status = tool_call.get('status', 'unknown')
                                print(f"Tool executed: {tool_name}, Status: {status}")

                                if tool_name == 'update_task':
                                    print("✓ Update task functionality is working!")
                                else:
                                    print(f"⚠ Expected update_task, got {tool_name}")
                        else:
                            print("⚠ No tool calls executed for update")

                    # Step 3: Show tasks to verify update
                    print(f"\nStep 3: Showing tasks to verify update")
                    show_payload = {
                        "conversation_id": None,
                        "message": "show my tasks"
                    }

                    show_resp = requests.post(
                        f"{base_url}/api/chat/{user_id}",
                        json=show_payload,
                        headers=headers
                    )

                    if show_resp.status_code == 200:
                        show_response_data = show_resp.json()
                        print(f"Show response: {show_response_data.get('response', 'No response')[:150]}...")
                    else:
                        print(f"Show tasks failed: {show_resp.status_code}")
                else:
                    print(f"Add task failed: {add_resp.status_code}")

            else:
                print(f"Login failed: {login_resp.status_code}")
        else:
            print(f"Registration failed: {register_resp.status_code}")

    except requests.exceptions.ConnectionError:
        print("Could not connect to server. Is the backend running on http://127.0.0.1:8000?")
    except Exception as e:
        print(f"Error during testing: {e}")

if __name__ == "__main__":
    test_update_simple()