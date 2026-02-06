@echo off
echo =========================================
echo CHATBOT FUNCTIONALITY VERIFICATION
echo =========================================

echo 1. Checking backend configuration...
cd backend

REM Read the configuration values
for /f "tokens=2 delims==" %%a in ('findstr "AI_PROVIDER=" .env') do set AI_PROVIDER=%%a
for /f "tokens=2 delims==" %%a in ('findstr "OPENROUTER_API_KEY=" .env') do set OPENROUTER_KEY=%%a
for /f "tokens=2 delims==" %%a in ('findstr "OPENROUTER_BASE_URL=" .env') do set OPENROUTER_BASE_URL=%%a

echo    AI_PROVIDER: %AI_PROVIDER%
echo    OPENROUTER_BASE_URL: %OPENROUTER_BASE_URL%
echo    OPENROUTER_API_KEY:
if "%OPENROUTER_KEY%"=="your-openrouter-api-key-here" (
    echo PLACEHOLDER ^(needs to be replaced^)
) else if defined OPENROUTER_KEY (
    if %OPENROUTER_KEY:~0,5%==sk-or- (
        echo SET ^(valid format^)
    ) else (
        echo POSSIBLY INVALID FORMAT
    )
) else (
    echo NOT SET
)

echo.
echo 2. Configuration Status:
if "%AI_PROVIDER%"=="openrouter" if not "%OPENROUTER_KEY%"=="your-openrouter-api-key-here" if defined OPENROUTER_KEY (
    echo    ✅ Configuration is CORRECT
    echo    - AI_PROVIDER is set to openrouter
    echo    - OPENROUTER_API_KEY is set with a real value
    echo    - OPENROUTER_BASE_URL is correct
    echo.
    echo 3. REQUIRED ACTION:
    echo    🔄 Restart the backend server to apply configuration:
    echo       cd backend
    echo       uvicorn src.main:app --reload
    echo.
    echo    After restarting, the chatbot should work properly!
) else (
    echo    ❌ Configuration needs attention:
    if not "%AI_PROVIDER%"=="openrouter" (
        echo    - AI_PROVIDER is not set to 'openrouter'
    )
    if "%OPENROUTER_KEY%"=="your-openrouter-api-key-here" (
        echo    - OPENROUTER_API_KEY still has placeholder value
    )
    if not defined OPENROUTER_KEY (
        echo    - OPENROUTER_API_KEY is not set
    )
)

echo.
echo =========================================
echo SUMMARY
echo =========================================
echo If configuration is correct but chatbot still shows error:
echo - Stop any running backend server
echo - Start backend with: uvicorn src.main:app --reload
echo - Refresh frontend browser
echo - Test chatbot commands again
echo =========================================