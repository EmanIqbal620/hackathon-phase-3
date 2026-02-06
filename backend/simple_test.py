import sys
import os
sys.path.insert(0, os.path.join(os.getcwd(), 'src'))

# Test the configuration
from src.config import config
print("Current configuration:")
print(f"AI_PROVIDER: {config.AI_PROVIDER}")
print(f"OPENROUTER_API_KEY: {'SET' if config.OPENROUTER_API_KEY else 'NOT SET'}")
print(f"OPENAI_API_KEY: {'SET' if config.OPENAI_API_KEY else 'NOT SET'}")
print()

# Test imports
try:
    from src.agents.chat_agent import process_chat_request, ChatRequest
    print("✓ Chat agent imports successfully")
except ImportError as e:
    print(f"✗ Chat agent import failed: {e}")

try:
    from src.mcp_tools.add_task import add_task
    print("✓ MCP tools import successfully")
except ImportError as e:
    print(f"✗ MCP tools import failed: {e}")

# Test the fallback functionality
try:
    from src.agents.chat_agent_mock_fallback import process_chat_request_with_fallback
    print("✓ Fallback agent imports successfully")
except ImportError as e:
    print(f"✗ Fallback agent import failed: {e}")

print()
print("Configuration summary:")
if config.OPENROUTER_API_KEY:
    print("- OpenRouter API key is configured")
elif config.OPENAI_API_KEY:
    print("- OpenAI API key is configured")
else:
    print("- No API keys configured (will use fallback mode)")

print(f"- Current provider: {config.AI_PROVIDER}")