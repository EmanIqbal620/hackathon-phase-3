#!/usr/bin/env python3
"""Simple test to check if models can be imported without errors"""

print("Testing model imports...")

try:
    from src.models.user import User
    print("[OK] User model imported successfully")

    from src.models.conversation import Conversation, Message
    print("[OK] Conversation and Message models imported successfully")

    from src.models.task import Task
    print("[OK] Task model imported successfully")

    print("\nAll models imported successfully!")

    # Test creating instances
    import uuid
    user_id = str(uuid.uuid4())
    user = User(email="test@test.com", password_hash="hash")
    print(f"[OK] User instance created: {user.email}")

    conv = Conversation(user_id=user_id, title="Test Conversation")
    print(f"[OK] Conversation instance created: {conv.title}")

    msg = Message(user_id=user_id, conversation_id=1, role="user", content="Hello")
    print(f"[OK] Message instance created: {msg.content}")

    print("\n[OK] All tests passed!")

except Exception as e:
    print(f"[ERROR] Error: {e}")
    import traceback
    traceback.print_exc()