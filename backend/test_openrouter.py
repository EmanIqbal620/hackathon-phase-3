import os
from openai import OpenAI
from src.config import config

print("Testing OpenRouter Connection...")
print(f"AI_PROVIDER: {config.AI_PROVIDER}")
print(f"OPENROUTER_API_KEY: {'SET' if config.OPENROUTER_API_KEY else 'NOT SET'}")
print(f"OPENROUTER_BASE_URL: {config.OPENROUTER_BASE_URL}")
print(f"OPENROUTER_MODEL: {config.OPENROUTER_MODEL}")
print()

if config.OPENROUTER_API_KEY:
    try:
        print("Creating OpenRouter client...")
        client = OpenAI(
            api_key=config.OPENROUTER_API_KEY,
            base_url=config.OPENROUTER_BASE_URL
        )

        print("Testing a simple request...")
        response = client.chat.completions.create(
            model=config.OPENROUTER_MODEL,
            messages=[{"role": "user", "content": "Hello, just testing connection. Respond with 'OK'."}],
            max_tokens=10
        )

        result = response.choices[0].message.content
        print(f"SUCCESS: {result}")
        print("OpenRouter connection is working!")

    except Exception as e:
        print(f"ERROR connecting to OpenRouter: {e}")
        print("This explains why the chatbot is in fallback mode.")
else:
    print("OpenRouter API key is not set.")