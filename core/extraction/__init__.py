"""
Code extraction module for temporary email service.

This module provides functionality to extract various types of codes
from email messages, including OTP codes, verification URLs, and tokens.
"""

from .code_extractor import CodeExtractor
from .patterns import (
    OTP_4_PATTERN,
    OTP_5_PATTERN,
    OTP_6_PATTERN,
    OTP_8_PATTERN,
    VERIFICATION_URL_PATTERN,
    TOKEN_PATTERN,
    RECOVERY_CODE_PATTERN,
    GOOGLE_AUTH_PATTERN,
    CODE_KEYWORD_PATTERN,
    ALL_PATTERNS
)

__all__ = [
    'CodeExtractor',
    'OTP_4_PATTERN',
    'OTP_5_PATTERN', 
    'OTP_6_PATTERN',
    'OTP_8_PATTERN',
    'VERIFICATION_URL_PATTERN',
    'TOKEN_PATTERN',
    'RECOVERY_CODE_PATTERN',
    'GOOGLE_AUTH_PATTERN',
    'CODE_KEYWORD_PATTERN',
    'ALL_PATTERNS'
]