import re

def validate_email(email):
    """
    Validate email format
    """
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def validate_password(password):
    """
    Validate password strength
    """
    if len(password) < 8:
        return False
    return True

def validate_phone(phone):
    """
    Validate phone number format
    """
    # Basic phone validation - can be enhanced based on requirements
    pattern = r'^\+?1?\d{9,15}$'
    return re.match(pattern, phone) is not None