"""
Validation utilities for extracted codes.

This module provides functions to validate and filter extracted codes
to reduce false positives and improve accuracy.
"""

import re
from typing import List, Set, Optional
from datetime import datetime


def is_likely_otp(code: str) -> bool:
    """
    Check if a code is likely an OTP.
    
    Args:
        code: The code to validate
        
    Returns:
        True if the code appears to be a valid OTP
    """
    # Remove any non-digit characters
    digits = re.sub(r'\D', '', code)
    
    # OTP codes are typically 4-8 digits
    if len(digits) < 4 or len(digits) > 8:
        return False
    
    # Avoid obvious patterns like 111111, 123456, 000000
    if digits in {'1111', '2222', '3333', '4444', '5555', '6666', '7777', '8888', '9999', '0000',
                  '11111', '22222', '33333', '44444', '55555', '66666', '77777', '88888', '99999', '00000',
                  '111111', '222222', '333333', '444444', '555555', '666666', '777777', '888888', '999999', '000000',
                  '1234', '12345', '123456', '1234567', '12345678'}:
        return False
    
    # Check for repeating patterns (e.g., 121212, 343434)
    if len(digits) >= 6 and digits[:3] == digits[3:6]:
        return False
    
    return True


def is_likely_url(url: str) -> bool:
    """
    Check if a URL is likely a verification URL.
    
    Args:
        url: The URL to validate
        
    Returns:
        True if the URL appears to be a verification URL
    """
    url_lower = url.lower()
    
    # Must contain verification-related keywords
    verification_keywords = {
        'verify', 'verification', 'confirm', 'confirmation', 
        'activate', 'activation', 'auth', 'authenticate',
        'token', 'code', 'otp', '2fa', 'login', 'signin'
    }
    
    has_keyword = any(keyword in url_lower for keyword in verification_keywords)
    
    # Must be a valid HTTP/HTTPS URL
    is_valid_url = url.startswith(('http://', 'https://'))
    
    return has_keyword and is_valid_url


def is_likely_token(token: str) -> bool:
    """
    Check if a string is likely an authentication token.
    
    Args:
        token: The token to validate
        
    Returns:
        True if the string appears to be a valid token
    """
    # Remove any non-alphanumeric characters
    clean_token = re.sub(r'[^a-zA-Z0-9]', '', token)
    
    # Tokens are typically 8-32 characters
    if len(clean_token) < 8 or len(clean_token) > 32:
        return False
    
    # Avoid common words or patterns
    common_words = {
        'test', 'demo', 'sample', 'example', 'verification', 'confirmation',
        'authenticate', 'authorization', 'temporary', 'session', 'cookie'
    }
    
    if clean_token.lower() in common_words:
        return False
    
    # Should have a mix of letters and numbers (not all one type)
    has_letters = bool(re.search(r'[a-zA-Z]', clean_token))
    has_numbers = bool(re.search(r'\d', clean_token))
    
    return has_letters or has_numbers


def is_likely_recovery_code(code: str) -> bool:
    """
    Check if a code is likely a recovery code.
    
    Args:
        code: The code to validate
        
    Returns:
        True if the code appears to be a valid recovery code
    """
    # Clean the code (remove spaces and hyphens)
    clean_code = re.sub(r'[-\s]', '', code.upper())
    
    # Recovery codes are typically 12-16 characters for proper format
    if len(clean_code) < 12 or len(clean_code) > 16:
        return False
    
    # Should be alphanumeric
    if not re.match(r'^[A-Z0-9]+$', clean_code):
        return False
    
    # Avoid common words
    common_words = {
        'VERIFICATION', 'CONFIRMATION', 'AUTHENTICATE', 'TEMPORARY',
        'SECURITY', 'ACCOUNT', 'PASSWORD', 'RECOVERY'
    }
    
    if clean_code in common_words:
        return False
    
    # Should have a good mix of letters and numbers (not all one type)
    has_letters = bool(re.search(r'[A-Z]', clean_code))
    has_numbers = bool(re.search(r'[0-9]', clean_code))
    
    return has_letters and has_numbers


def filter_duplicate_codes(codes: List[str]) -> List[str]:
    """
    Remove duplicate codes while preserving order.
    
    Args:
        codes: List of codes to deduplicate
        
    Returns:
        List of unique codes in original order
    """
    seen: Set[str] = set()
    unique_codes = []
    
    for code in codes:
        if code not in seen:
            seen.add(code)
            unique_codes.append(code)
    
    return unique_codes


def validate_code_by_type(code: str, code_type: str) -> bool:
    """
    Validate a code based on its type.
    
    Args:
        code: The code to validate
        code_type: The type of code ('otp_4', 'otp_5', 'otp_6', 'otp_8', 
                   'verification_url', 'token', 'recovery_code', 'google_auth', 'code_keyword')
        
    Returns:
        True if the code is valid for its type
    """
    validators = {
        'otp_4': lambda c: is_likely_otp(c) and len(re.sub(r'\D', '', c)) == 4,
        'otp_5': lambda c: is_likely_otp(c) and len(re.sub(r'\D', '', c)) == 5,
        'otp_6': lambda c: is_likely_otp(c) and len(re.sub(r'\D', '', c)) == 6,
        'otp_8': lambda c: is_likely_otp(c) and len(re.sub(r'\D', '', c)) == 8,
        'verification_url': is_likely_url,
        'token': is_likely_token,
        'recovery_code': is_likely_recovery_code,
        'google_auth': lambda c: is_likely_otp(c) and len(re.sub(r'\D', '', c)) == 6,
        'code_keyword': is_likely_otp,
    }
    
    validator = validators.get(code_type)
    if not validator:
        return False
    
    return validator(code)


def calculate_confidence_score(code: str, code_type: str, context: str = "") -> float:
    """
    Calculate a confidence score for an extracted code.
    
    Args:
        code: The extracted code
        code_type: The type of code
        context: The surrounding text context
        
    Returns:
        Confidence score between 0.0 and 1.0
    """
    base_score = 0.5  # Base confidence
    
    # Higher confidence for codes with explicit keywords
    if code_type in ['code_keyword', 'google_auth']:
        base_score += 0.3
    
    # Higher confidence for URLs with clear verification keywords
    if code_type == 'verification_url':
        context_lower = context.lower()
        if any(keyword in context_lower for keyword in ['verify', 'confirm', 'activate']):
            base_score += 0.3
    
    # Higher confidence for OTP codes of typical lengths
    if code_type in ['otp_4', 'otp_5', 'otp_6', 'otp_8']:
        digits = re.sub(r'\D', '', code)
        if len(digits) in [4, 6]:  # Most common OTP lengths
            base_score += 0.2
    
    # Lower confidence for generic tokens
    if code_type == 'token':
        base_score -= 0.1
    
    # Adjust based on validation
    if validate_code_by_type(code, code_type):
        base_score += 0.2
    else:
        base_score -= 0.3
    
    # Ensure score is within bounds
    return max(0.0, min(1.0, base_score))