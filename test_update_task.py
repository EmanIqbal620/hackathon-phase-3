#!/usr/bin/env python3
"""
Test script to verify update task functionality in chatbot.
"""

import requests
import json
import time

def test_update_task():
    base_url = "http://127.0.0.1:8000"

    print("Testing update task functionality...")

    try:
        # Register a new test user
        test_email = f"test_update_{int(time.time())}@example.com"
        register_data = {
            "name": "Test User",
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

                # First, add a task to update
                print("\n--- Adding a task to update ---")
                add_payload = {
                    "conversation_id": None,
                    "message": "Add a task to study mathematics"
                }

                add_resp = requests.post(
                    f"{base_url}/api/chat/{user_id}",
                    json=add_payload,
                    headers=headers
                )

                if add_resp.status_code == 200:
                    add_response_data = add_resp.json()
                    response_text = add_response_data.get('response', 'No response')
                    safe_response = response_text.encode('ascii', 'ignore').decode('ascii')
                    print(f"Add task response: {safe_response}")

                    # Now try to update the task using different formats
                    update_formats = [
                        {"message": "update first task to study physics"},
                        {"message": "update task study to study chemistry"},
                        {"message": "update the study mathematics task to study biology"},
                        {"message": "change first task to study computer science"}
                    ]

                    for i, update_cmd in enumerate(update_formats):
                        print(f"\n--- Testing update format {i+1}: {update_cmd['message']} ---")

                        update_payload = {
                            "conversation_id": None,  # Could use conversation ID from previous response
                            "message": update_cmd['message']
                        }

                        update_resp = requests.post(
                            f"{base_url}/api/chat/{user_id}",
                            json=update_payload,
                            headers=headers
                        )

                        print(f"Status: {update_resp.status_code}")

                        if update_resp.status_code == 200:
                            response_data = update_resp.json()
                            response_text = response_data.get('response', 'No response')
                            safe_response = response_text.encode('ascii', 'ignore').decode('ascii')
                            print(f"AI Response: {safe_response}")

                            if response_data.get('tool_calls'):
                                print(f"Tool Calls: {len(response_data['tool_calls'])} executed")
                                for tool_call in response_data['tool_calls']:
                                    print(f"  - Tool: {tool_call.get('tool', 'unknown')}, Status: {tool_call.get('status', 'unknown')}")
                        else:
                            error_text = update_resp.text.encode('ascii', 'ignore').decode('ascii')
                            print(f"Error: {error_text}")

                        time.sleep(1)
                else:
                    print(f"Failed to add initial task: {add_resp.status_code}, {add_resp.text}")

            else:
                print(f"Login failed: {login_resp.status_code}, {login_resp.text}")
        else:
            print(f"Registration failed: {register_resp.status_code}, {register_resp.text}")

    except requests.exceptions.ConnectionError:
        print("Could not connect to server. Is the backend running on http://127.0.0.1:8000?")
    except Exception as e:
        print(f"Error during testing: {e}")

if __name__ == "__main__":
    test_update_task()