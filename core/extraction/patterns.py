"""
Regular expression patterns for code extraction.

This module contains compiled regex patterns for various types of codes
that might be found in email messages.
"""

import re
from typing import Dict, Pattern

# 4-digit OTP codes (e.g., "1234")
OTP_4_PATTERN: Pattern = re.compile(r'\b\d{4}\b')

# 5-digit OTP codes (e.g., "12345")
OTP_5_PATTERN: Pattern = re.compile(r'\b\d{5}\b')

# 6-digit OTP codes (e.g., "123456")
OTP_6_PATTERN: Pattern = re.compile(r'\b\d{6}\b')

# 8-digit OTP codes (e.g., "12345678")
OTP_8_PATTERN: Pattern = re.compile(r'\b\d{8}\b')

# Verification URLs (http/https links with verification/confirm keywords)
VERIFICATION_URL_PATTERN: Pattern = re.compile(
    r'\bhttps?://[^\s<>"]+(?:verification|verify|confirm|activate)[^\s<>"]*\b',
    re.IGNORECASE
)

# Alphanumeric tokens (6-32 chars, letters and numbers)
TOKEN_PATTERN: Pattern = re.compile(r'\b[a-zA-Z0-9]{6,32}\b')

# Recovery codes (e.g., "AB12-CD34-EF56" or groups of 4 chars)
RECOVERY_CODE_PATTERN: Pattern = re.compile(
    r'\b(?:[A-Z0-9]{4}[-\s]){2,}[A-Z0-9]{4}\b|\b[A-Z0-9]{12,}\b',
    re.IGNORECASE
)

# Google Authenticator codes (6-digit, often with "Google" context)
GOOGLE_AUTH_PATTERN: Pattern = re.compile(
    r'\b(?:google|authenticator|2fa|two.?factor)[^\d]*(\d{6})\b',
    re.IGNORECASE
)

# Codes with keywords (e.g., "code: 123456", "verification code is")
CODE_KEYWORD_PATTERN: Pattern = re.compile(
    r'\b(?:code|código|verification|verify|confirm|pin|otp)[\s:]+(\d{4,8})\b',
    re.IGNORECASE
)

# All patterns dictionary for easy reference
ALL_PATTERNS: Dict[str, Pattern] = {
    'otp_4': OTP_4_PATTERN,
    'otp_5': OTP_5_PATTERN,
    'otp_6': OTP_6_PATTERN,
    'otp_8': OTP_8_PATTERN,
    'verification_url': VERIFICATION_URL_PATTERN,
    'token': TOKEN_PATTERN,
    'recovery_code': RECOVERY_CODE_PATTERN,
    'google_auth': GOOGLE_AUTH_PATTERN,
    'code_keyword': CODE_KEYWORD_PATTERN,
}

# Pattern descriptions for documentation
PATTERN_DESCRIPTIONS = {
    'otp_4': '4-digit OTP code (e.g., 1234)',
    'otp_5': '5-digit OTP code (e.g., 12345)',
    'otp_6': '6-digit OTP code (e.g., 123456)',
    'otp_8': '8-digit OTP code (e.g., 12345678)',
    'verification_url': 'Verification/confirm URL',
    'token': 'Alphanumeric token (6-32 chars)',
    'recovery_code': 'Recovery code (e.g., AB12-CD34-EF56)',
    'google_auth': 'Google Authenticator code',
    'code_keyword': 'Code with keyword (e.g., "code: 123456")',
}