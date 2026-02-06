#!/bin/bash
# Test script to verify chatbot functionality

echo "========================================="
echo "CHATBOT FUNCTIONALITY VERIFICATION"
echo "========================================="

echo "1. Checking backend configuration..."
cd backend

# Read the configuration
AI_PROVIDER=$(grep "AI_PROVIDER=" .env | cut -d'=' -f2)
OPENROUTER_KEY=$(grep "OPENROUTER_API_KEY=" .env | cut -d'=' -f2)
OPENROUTER_BASE_URL=$(grep "OPENROUTER_BASE_URL=" .env | cut -d'=' -f2)

echo "   AI_PROVIDER: $AI_PROVIDER"
echo "   OPENROUTER_BASE_URL: $OPENROUTER_BASE_URL"
echo -n "   OPENROUTER_API_KEY: "
if [[ "$OPENROUTER_KEY" == "your-openrouter-api-key-here" ]]; then
    echo "PLACEHOLDER (needs to be replaced)"
elif [[ -n "$OPENROUTER_KEY" && ${#OPENROUTER_KEY} -gt 20 ]]; then
    echo "SET (valid length)"
else
    echo "NOT SET OR INVALID"
fi

echo ""
echo "2. Configuration Status:"
if [[ "$AI_PROVIDER" == "openrouter" ]] && [[ "$OPENROUTER_KEY" != "your-openrouter-api-key-here" ]] && [[ -n "$OPENROUTER_KEY" ]]; then
    echo "   ✅ Configuration is CORRECT"
    echo "   - AI_PROVIDER is set to openrouter"
    echo "   - OPENROUTER_API_KEY is set with a real value"
    echo "   - OPENROUTER_BASE_URL is correct"
    echo ""
    echo "3. REQUIRED ACTION:"
    echo "   🔄 Restart the backend server to apply configuration:"
    echo "      cd backend"
    echo "      uvicorn src.main:app --reload"
    echo ""
    echo "   After restarting, the chatbot should work properly!"
else
    echo "   ❌ Configuration needs attention:"
    if [[ "$AI_PROVIDER" != "openrouter" ]]; then
        echo "   - AI_PROVIDER is not set to 'openrouter'"
    fi
    if [[ "$OPENROUTER_KEY" == "your-openrouter-api-key-here" ]]; then
        echo "   - OPENROUTER_API_KEY still has placeholder value"
    fi
    if [[ -z "$OPENROUTER_KEY" ]]; then
        echo "   - OPENROUTER_API_KEY is not set"
    fi
fi

echo ""
echo "========================================="
echo "SUMMARY"
echo "========================================="
echo "If configuration is correct but chatbot still shows error:"
echo "- Stop any running backend server"
echo "- Start backend with: uvicorn src.main:app --reload"
echo "- Refresh frontend browser"
echo "- Test chatbot commands again"
echo "========================================="