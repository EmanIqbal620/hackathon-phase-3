from setuptools import setup, find_packages

setup(
    name="todo-backend",
    version="1.0.0",
    packages=find_packages(),
    install_requires=[
        "fastapi>=0.104.1",
        "uvicorn>=0.24.0",
        "sqlmodel>=0.0.16",
        "aiosqlite>=0.19.0",
        "python-jose[cryptography]>=3.3.0",
        "passlib[bcrypt]>=1.7.4",
        "python-multipart>=0.0.6",
        "python-dotenv>=1.0.0",
        "pydantic>=2.5.0",
        "openai>=1.3.7",
        "mcp>=1.0.0",
    ],
    python_requires=">=3.9",
)