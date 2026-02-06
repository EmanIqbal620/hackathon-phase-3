#!/usr/bin/env python3
"""
Test script to verify chatbot functionality for task operations.
"""

import requests
import json
import time

def test_chatbot_commands():
    base_url = "http://127.0.0.1:8000"

    # First, let's try to register a test user or login
    print("Testing chatbot functionality...")

    try:
        # First, let's try to register a new test user
        test_email = f"test_{int(time.time())}@example.com"
        register_data = {
            "name": "Test User",
            "email": test_email,
            "password": "testpassword123"
        }

        print(f"Attempting to register test user: {test_email}")

        # Register the test user
        register_resp = requests.post(f"{base_url}/api/auth/register", json=register_data)
        print(f"Registration response: {register_resp.status_code}")

        if register_resp.status_code == 200 or register_resp.status_code == 201:
            auth_data = register_resp.json()
            user_id = auth_data.get('user_id', 'unknown')

            # Now login to get the token
            login_data = {
                "email": test_email,
                "password": "testpassword123"
            }

            login_resp = requests.post(f"{base_url}/api/auth/login", json=login_data)
            if login_resp.status_code == 200:
                login_response = login_resp.json()
                token = login_response.get('access_token', '')

                print(f"Registered and logged in user: {user_id}")

                # Test various chat commands
                headers = {
                    'Authorization': f'Bearer {token}',
                    'Content-Type': 'application/json'
                }

                # Test commands that should work based on the AI agent service
                test_commands = [
                    {"message": "Add a task to buy groceries"},
                    {"message": "Show my tasks"},
                    {"message": "Add a task to complete homework"},
                    {"message": "Mark first task as complete"},
                    {"message": "Delete first task"}
                ]

                for i, cmd in enumerate(test_commands):
                    print(f"\n--- Testing command {i+1}: {cmd['message']} ---")

                    chat_payload = {
                        "conversation_id": None,  # New conversation
                        "message": cmd['message']
                    }

                    # Send the command to the chat endpoint
                    chat_resp = requests.post(
                        f"{base_url}/api/chat/{user_id}",
                        json=chat_payload,
                        headers=headers
                    )

                    print(f"Status: {chat_resp.status_code}")

                    if chat_resp.status_code == 200:
                        response_data = chat_resp.json()
                        response_text = response_data.get('response', 'No response')
                        # Remove or replace problematic characters for console output
                        safe_response = response_text.encode('ascii', 'ignore').decode('ascii')
                        print(f"AI Response: {safe_response}")

                        if response_data.get('tool_calls'):
                            print(f"Tool Calls: {len(response_data['tool_calls'])} executed")
                            for tool_call in response_data['tool_calls']:
                                print(f"  - Tool: {tool_call.get('tool', 'unknown')}, Status: {tool_call.get('status', 'unknown')}")
                    else:
                        error_text = chat_resp.text.encode('ascii', 'ignore').decode('ascii')
                        print(f"Error: {error_text}")

                    # Small delay between requests
                    time.sleep(1)
            else:
                print(f"Login failed after registration: {login_resp.status_code}, {login_resp.text}")

        else:
            print(f"Registration failed: {register_resp.status_code}, {register_resp.text}")

            # Try with the known user from logs if registration fails
            print("\nTrying with login (maira@gmail.com)...")
            login_resp = requests.post(f"{base_url}/api/auth/login", json={
                "email": "maira@gmail.com",
                "password": "your_actual_password_here"  # This would need to be the real password
            })

            if login_resp.status_code == 200:
                login_data = login_resp.json()
                token = login_data.get('access_token')
                user_id = login_data.get('user_id', 'unknown')

                print(f"Logged in as user: {user_id}")

                headers = {
                    'Authorization': f'Bearer {token}',
                    'Content-Type': 'application/json'
                }

                # Test commands
                test_commands = [
                    {"message": "Add a task to buy groceries"},
                    {"message": "Show my tasks"},
                ]

                for i, cmd in enumerate(test_commands):
                    print(f"\n--- Testing command {i+1}: {cmd['message']} ---")

                    chat_payload = {
                        "conversation_id": None,
                        "message": cmd['message']
                    }

                    chat_resp = requests.post(
                        f"{base_url}/api/chat/{user_id}",
                        json=chat_payload,
                        headers=headers
                    )

                    print(f"Status: {chat_resp.status_code}")

                    if chat_resp.status_code == 200:
                        response_data = chat_resp.json()
                        response_text = response_data.get('response', 'No response')
                        # Remove or replace problematic characters for console output
                        safe_response = response_text.encode('ascii', 'ignore').decode('ascii')
                        print(f"AI Response: {safe_response}")

                        if response_data.get('tool_calls'):
                            print(f"Tool Calls: {len(response_data['tool_calls'])} executed")
                            for tool_call in response_data['tool_calls']:
                                print(f"  - Tool: {tool_call.get('tool', 'unknown')}, Status: {tool_call.get('status', 'unknown')}")
                    else:
                        error_text = chat_resp.text.encode('ascii', 'ignore').decode('ascii')
                        print(f"Error: {error_text}")

                    time.sleep(1)
            else:
                print(f"Could not authenticate. Login failed: {login_resp.status_code}, {login_resp.text}")

    except requests.exceptions.ConnectionError:
        print("Could not connect to server. Is the backend running on http://127.0.0.1:8000?")
    except Exception as e:
        print(f"Error during testing: {e}")

if __name__ == "__main__":
    test_chatbot_commands()