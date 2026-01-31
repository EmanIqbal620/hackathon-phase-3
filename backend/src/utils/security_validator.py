"""
Security Validation Utilities
This module provides functions for validating user inputs and parameters to prevent common security vulnerabilities.
"""
from typing import Any, Optional, Union
import re
import html
import urllib.parse
from pydantic import BaseModel, validator, ValidationError
from enum import Enum


class InputType(Enum):
    """Enumeration of input types for validation"""
    USERNAME = "username"
    EMAIL = "email"
    PASSWORD = "password"
    TEXT = "text"
    NUMBER = "number"
    URL = "url"
    ID = "id"
    SEARCH = "search"


class SecurityValidator:
    """Utility class for input validation and sanitization"""

    @staticmethod
    def sanitize_string(value: str) -> str:
        """
        Sanitize a string to prevent XSS and other injection attacks.

        Args:
            value: Input string to sanitize

        Returns:
            Sanitized string
        """
        if not isinstance(value, str):
            raise TypeError("Input must be a string")

        # Remove null bytes
        sanitized = value.replace('\x00', '')

        # HTML encode special characters
        sanitized = html.escape(sanitized)

        # Strip leading/trailing whitespace
        sanitized = sanitized.strip()

        return sanitized

    @staticmethod
    def validate_username(username: str) -> tuple[bool, str]:
        """
        Validate username according to security standards.

        Args:
            username: Username to validate

        Returns:
            Tuple of (is_valid, error_message)
        """
        if not username:
            return False, "Username is required"

        if len(username) < 3:
            return False, "Username must be at least 3 characters long"

        if len(username) > 50:
            return False, "Username must be no more than 50 characters long"

        # Allow letters, numbers, underscores, hyphens, and periods
        if not re.match(r'^[a-zA-Z0-9_.-]+$', username):
            return False, "Username can only contain letters, numbers, underscores, hyphens, and periods"

        # Check for potential SQL injection patterns
        sql_patterns = [
            r'select\b', r'union\b', r'drop\b', r'insert\b',
            r'update\b', r'delete\b', r'exec\b', r'execute\b'
        ]

        for pattern in sql_patterns:
            if re.search(pattern, username, re.IGNORECASE):
                return False, "Username contains invalid characters or patterns"

        return True, ""

    @staticmethod
    def validate_email(email: str) -> tuple[bool, str]:
        """
        Validate email address format and security.

        Args:
            email: Email address to validate

        Returns:
            Tuple of (is_valid, error_message)
        """
        if not email:
            return False, "Email is required"

        if len(email) > 254:
            return False, "Email is too long"

        # RFC 5322 compliant email regex (simplified)
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'

        if not re.match(email_pattern, email):
            return False, "Invalid email format"

        # Check for potential XSS patterns
        xss_patterns = [
            r'<script', r'javascript:', r'on\w+\s*=',
            r'<iframe', r'<object', r'<embed'
        ]

        for pattern in xss_patterns:
            if re.search(pattern, email, re.IGNORECASE):
                return False, "Email contains potential security threats"

        return True, ""

    @staticmethod
    def validate_password(password: str) -> tuple[bool, str]:
        """
        Validate password strength and security.

        Args:
            password: Password to validate

        Returns:
            Tuple of (is_valid, error_message)
        """
        if not password:
            return False, "Password is required"

        if len(password) < 8:
            return False, "Password must be at least 8 characters long"

        if len(password) > 128:
            return False, "Password is too long (maximum 128 characters)"

        # Check for required character types
        has_upper = bool(re.search(r'[A-Z]', password))
        has_lower = bool(re.search(r'[a-z]', password))
        has_digit = bool(re.search(r'\d', password))
        has_special = bool(re.search(r'[!@#$%^&*(),.?":{}|<>]', password))

        if not (has_upper and has_lower and has_digit and has_special):
            return False, "Password must contain uppercase, lowercase, digit, and special character"

        # Check for common passwords
        common_passwords = [
            'password', '123456', 'qwerty', 'admin', 'welcome',
            'login', 'user', 'hello', 'test', 'abc123'
        ]

        if password.lower() in common_passwords:
            return False, "Password is too common and not secure"

        return True, ""

    @staticmethod
    def validate_text(text: str, max_length: int = 1000) -> tuple[bool, str]:
        """
        Validate generic text input.

        Args:
            text: Text to validate
            max_length: Maximum allowed length

        Returns:
            Tuple of (is_valid, error_message)
        """
        if not text:
            return True, ""  # Allow empty text

        if len(text) > max_length:
            return False, f"Text exceeds maximum length of {max_length} characters"

        # Check for potential XSS patterns
        xss_patterns = [
            r'<script', r'javascript:', r'on\w+\s*=',
            r'<iframe', r'<object', r'<embed', r'<meta',
            r'data:', r'vbscript:', r'expression\('
        ]

        for pattern in xss_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                return False, "Text contains potential security threats"

        # Check for SQL injection patterns
        sql_patterns = [
            r'\b(select|union|drop|insert|update|delete|exec|execute|script)\b',
            r'(\b|\s)(and|or)(\s|\b)',
            r'\'\s*(=|<|>|!|LIKE)',
            r'(\b|\s)(OR|AND)(\s|\b).*?=.*?.*?=.*?',
            r'UNION\s+SELECT',
            r'SLEEP\(',
            r'BENCHMARK\('
        ]

        for pattern in sql_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                return False, "Text contains potential SQL injection patterns"

        return True, ""

    @staticmethod
    def validate_numeric(value: Union[str, int, float], min_val: Optional[float] = None, max_val: Optional[float] = None) -> tuple[bool, str]:
        """
        Validate numeric input.

        Args:
            value: Numeric value to validate
            min_val: Minimum allowed value
            max_val: Maximum allowed value

        Returns:
            Tuple of (is_valid, error_message)
        """
        try:
            num_value = float(value)
        except (TypeError, ValueError):
            return False, "Value must be a number"

        if min_val is not None and num_value < min_val:
            return False, f"Value must be greater than or equal to {min_val}"

        if max_val is not None and num_value > max_val:
            return False, f"Value must be less than or equal to {max_val}"

        return True, ""

    @staticmethod
    def validate_url(url: str) -> tuple[bool, str]:
        """
        Validate URL format and security.

        Args:
            url: URL to validate

        Returns:
            Tuple of (is_valid, error_message)
        """
        if not url:
            return False, "URL is required"

        if len(url) > 2048:  # Standard max URL length
            return False, "URL is too long"

        # Basic URL format validation
        try:
            parsed = urllib.parse.urlparse(url)
            if not parsed.scheme or not parsed.netloc:
                return False, "Invalid URL format"
        except Exception:
            return False, "Invalid URL format"

        # Check for dangerous protocols
        dangerous_protocols = ['javascript:', 'vbscript:', 'data:', 'file:']
        lower_url = url.lower()

        for protocol in dangerous_protocols:
            if lower_url.startswith(protocol):
                return False, f"URL uses potentially dangerous protocol: {protocol}"

        # Check for potential XSS in URL
        xss_patterns = [
            r'<script', r'javascript:', r'on\w+\s*=',
            r'<iframe', r'<object', r'<embed'
        ]

        for pattern in xss_patterns:
            if re.search(pattern, url, re.IGNORECASE):
                return False, "URL contains potential security threats"

        return True, ""

    @staticmethod
    def validate_id(id_value: str, id_type: str = "generic") -> tuple[bool, str]:
        """
        Validate ID formats based on type.

        Args:
            id_value: ID value to validate
            id_type: Type of ID (e.g., "uuid", "numeric", "alphanumeric")

        Returns:
            Tuple of (is_valid, error_message)
        """
        if not id_value:
            return False, "ID is required"

        if id_type == "uuid":
            # UUID format validation
            uuid_pattern = r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$'
            if not re.match(uuid_pattern, id_value, re.IGNORECASE):
                return False, "Invalid UUID format"
        elif id_type == "numeric":
            # Numeric ID validation
            if not re.match(r'^\d+$', id_value):
                return False, "Numeric ID must contain only digits"
        elif id_type == "alphanumeric":
            # Alphanumeric ID validation
            if not re.match(r'^[a-zA-Z0-9]+$', id_value):
                return False, "Alphanumeric ID must contain only letters and digits"
        else:
            # Generic validation - alphanumeric with hyphens and underscores
            if not re.match(r'^[a-zA-Z0-9_-]+$', id_value):
                return False, "ID contains invalid characters"

        # Check for potential traversal attacks
        if '..' in id_value or '../' in id_value:
            return False, "ID contains path traversal sequences"

        return True, ""

    @staticmethod
    def validate_search_query(query: str) -> tuple[bool, str]:
        """
        Validate search query for security.

        Args:
            query: Search query to validate

        Returns:
            Tuple of (is_valid, error_message)
        """
        if not query:
            return True, ""  # Allow empty search

        if len(query) > 500:
            return False, "Search query is too long (maximum 500 characters)"

        # Check for SQL injection patterns in search
        sql_patterns = [
            r'\b(select|union|drop|insert|update|delete|exec|execute)\b',
            r'(\b|\s)(and|or)(\s|\b)',
            r'\'\s*(=|<|>|!|LIKE)',
            r'UNION\s+SELECT',
            r'SLEEP\(',
            r'BENCHMARK\('
        ]

        for pattern in sql_patterns:
            if re.search(pattern, query, re.IGNORECASE):
                return False, "Search query contains potential SQL injection patterns"

        return True, ""

    @staticmethod
    def validate_input_type(value: Any, input_type: InputType) -> tuple[bool, str]:
        """
        Validate input based on expected type.

        Args:
            value: Value to validate
            input_type: Expected input type

        Returns:
            Tuple of (is_valid, error_message)
        """
        if input_type == InputType.USERNAME:
            return SecurityValidator.validate_username(str(value))
        elif input_type == InputType.EMAIL:
            return SecurityValidator.validate_email(str(value))
        elif input_type == InputType.PASSWORD:
            return SecurityValidator.validate_password(str(value))
        elif input_type == InputType.TEXT:
            return SecurityValidator.validate_text(str(value))
        elif input_type == InputType.NUMBER:
            return SecurityValidator.validate_numeric(value)
        elif input_type == InputType.URL:
            return SecurityValidator.validate_url(str(value))
        elif input_type == InputType.ID:
            return SecurityValidator.validate_id(str(value))
        elif input_type == InputType.SEARCH:
            return SecurityValidator.validate_search_query(str(value))
        else:
            return True, ""


def validate_and_sanitize_input(value: Any, input_type: InputType) -> tuple[Any, bool, str]:
    """
    Validate and sanitize input value.

    Args:
        value: Value to validate and sanitize
        input_type: Type of input expected

    Returns:
        Tuple of (sanitized_value, is_valid, error_message)
    """
    # First sanitize if it's a string
    if isinstance(value, str):
        value = SecurityValidator.sanitize_string(value)

    # Then validate
    is_valid, error_msg = SecurityValidator.validate_input_type(value, input_type)

    return value, is_valid, error_msg


def validate_request_params(params: dict, schema: dict) -> tuple[dict, list[str]]:
    """
    Validate request parameters against a schema.

    Args:
        params: Dictionary of request parameters
        schema: Schema defining expected parameters and types

    Returns:
        Tuple of (validated_params, errors)
    """
    validated_params = {}
    errors = []

    for param_name, param_config in schema.items():
        value = params.get(param_name)
        required = param_config.get('required', False)
        input_type = param_config.get('type', InputType.TEXT)
        default = param_config.get('default')

        # Handle required fields
        if required and value is None:
            errors.append(f"Parameter '{param_name}' is required")
            continue

        # Use default if value is None and default exists
        if value is None and default is not None:
            value = default

        # Skip validation if value is None and not required
        if value is None:
            validated_params[param_name] = None
            continue

        # Validate and sanitize
        sanitized_value, is_valid, error_msg = validate_and_sanitize_input(value, input_type)

        if not is_valid:
            errors.append(f"Parameter '{param_name}': {error_msg}")
        else:
            validated_params[param_name] = sanitized_value

    return validated_params, errors


# Example usage and test cases
if __name__ == "__main__":
    # Test various validation functions
    test_cases = [
        ("valid_username", SecurityValidator.validate_username("john_doe")),
        ("invalid_username", SecurityValidator.validate_username("select * from users")),
        ("valid_email", SecurityValidator.validate_email("user@example.com")),
        ("invalid_email", SecurityValidator.validate_email("<script>alert('xss')</script>")),
        ("valid_password", SecurityValidator.validate_password("SecurePass123!")),
        ("invalid_password", SecurityValidator.validate_password("password")),
        ("safe_text", SecurityValidator.validate_text("This is safe text")),
        ("unsafe_text", SecurityValidator.validate_text("<script>alert('xss')</script>")),
    ]

    for test_name, (is_valid, error_msg) in test_cases:
        print(f"{test_name}: {'✓' if is_valid else '✗'} - {error_msg}")

    # Test parameter validation
    schema = {
        "username": {"type": InputType.USERNAME, "required": True},
        "email": {"type": InputType.EMAIL, "required": True},
        "bio": {"type": InputType.TEXT, "required": False},
        "age": {"type": InputType.NUMBER, "required": False},
    }

    test_params = {
        "username": "johndoe",
        "email": "john@example.com",
        "bio": "Software developer",
        "age": 30
    }

    validated, errors = validate_request_params(test_params, schema)
    print(f"\nParameter validation: {len(errors)} errors found")
    if errors:
        for error in errors:
            print(f"  - {error}")
    else:
        print("  All parameters valid!")
        print(f"  Validated params: {validated}")