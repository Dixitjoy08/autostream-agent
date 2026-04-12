"""
Tool functions for the agent, including lead capture
"""

def mock_lead_capture(name: str, email: str, platform: str) -> str:
    """
    Mock API function to capture lead information.
    In production, this would call a real CRM API (Salesforce, HubSpot, etc.)
    
    Args:
        name: Customer's full name
        email: Customer's email address
        platform: Content platform they use (YouTube, Instagram, etc.)
    
    Returns:
        Confirmation message
    """
    
    # Print to console with clear formatting
    print("\n" + "="*70)
    print("✓ LEAD CAPTURED SUCCESSFULLY")
    print("="*70)
    print(f"Name:     {name}")
    print(f"Email:    {email}")
    print(f"Platform: {platform}")
    print("="*70)
    print()
    
    return f"Lead captured: {name} ({email}) - Platform: {platform}"


def validate_email(email: str) -> bool:
    """
    Simple email validation.
    
    Args:
        email: Email address to validate
    
    Returns:
        True if email looks valid, False otherwise
    """
    return "@" in email and "." in email and len(email) > 5


def validate_name(name: str) -> bool:
    """
    Check if name is valid (not empty).
    
    Args:
        name: Name to validate
    
    Returns:
        True if name is valid, False otherwise
    """
    return len(name.strip()) >= 2


def validate_platform(platform: str, valid_platforms: list) -> bool:
    """
    Check if platform is in the list of supported platforms.
    
    Args:
        platform: Platform name to validate
        valid_platforms: List of valid platform names
    
    Returns:
        True if platform is supported, False otherwise
    """
    return platform.lower() in [p.lower() for p in valid_platforms]