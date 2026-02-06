# Chatbot Troubleshooting Guide

## Issue Description
The chatbot is showing the fallback message:
> "I'm having trouble connecting to my AI brain right now, but I can still help with basic task operations!"

## Root Cause Analysis
The issue occurs because the backend server is still running with the old configuration in memory, even though we've updated the API key in the .env file. The server needs to be restarted to pick up the new configuration.

## Current Configuration Status
✅ OpenRouter API key is now properly set in `backend/.env`
✅ AI_PROVIDER is set to `openrouter`
✅ MCP tools are properly configured
❌ Server has not been restarted to apply new configuration

## Immediate Action Required

### Step 1: Stop the Running Backend Server
1. Find the terminal/command prompt where the backend is running
2. Press `Ctrl+C` to stop the server

### Step 2: Start the Backend Server with New Configuration
```bash
cd backend
uvicorn src.main:app --reload
```

### Step 3: Verify the Server is Running
- Check that the server starts without errors
- Look for any API connection messages

### Step 4: Test the Chatbot
1. Refresh the frontend browser
2. Try the chatbot commands again:
   - "Update task watch"
   - "Mark task eman done"
   - "Add task buy groceries"
   - "Show my tasks"

## Why This Fixes the Issue
- The running server process caches the configuration at startup
- Even though we updated the .env file, the server is still using the old cached values
- Restarting forces the server to reload the configuration from the updated .env file
- This loads the valid OpenRouter API key and enables proper AI functionality

## Expected Results After Restart
- No more fallback error messages
- Faster response times
- MCP tools working properly
- Natural language processing working correctly
- Commands like "Update task watch" and "Mark task eman done" working as expected

## If Issues Persist After Restart
1. Verify the API key is still set correctly in `backend/.env`
2. Check network connectivity to OpenRouter
3. Confirm the model name `openrouter/auto` is valid
4. Check backend server logs for specific error messages

## Verification Commands
After restarting, you can test specific functionality:
- To update a task: "Update task 'eman' to 'eman completed'"
- To complete a task: "Complete task eman" or "Mark task eman done"
- To add a task: "Add task watch something"
- To list tasks: "Show my tasks"

## Server Restart Confirmation
After restarting the server, you should see log messages indicating successful connection to OpenRouter API.