"""
Code extractor for analyzing email messages and extracting various types of codes.

This module provides the main CodeExtractor class that can extract OTP codes,
verification URLs, tokens, and other codes from text and HTML content.
"""

import re
import html
from typing import List, Dict, Optional, Tuple, Any
from bs4 import BeautifulSoup

from .patterns import ALL_PATTERNS, PATTERN_DESCRIPTIONS
from .validators import (
    is_likely_otp,
    is_likely_url,
    is_likely_token,
    is_likely_recovery_code,
    filter_duplicate_codes,
    validate_code_by_type,
    calculate_confidence_score
)


class ExtractedCode:
    """Represents a code extracted from text."""
    
    def __init__(
        self,
        code: str,
        code_type: str,
        confidence: float,
        context: str = "",
        start_pos: int = 0,
        end_pos: int = 0
    ):
        self.code = code
        self.code_type = code_type
        self.confidence = confidence
        self.context = context
        self.start_pos = start_pos
        self.end_pos = end_pos
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            'code': self.code,
            'type': self.code_type,
            'confidence': self.confidence,
            'context': self.context,
            'start_pos': self.start_pos,
            'end_pos': self.end_pos
        }
    
    def __repr__(self) -> str:
        return f"ExtractedCode(code='{self.code}', type='{self.code_type}', confidence={self.confidence:.2f})"


class CodeExtractor:
    """
    Extracts various types of codes from text and HTML content.
    
    Supports extraction of:
    - OTP codes (4, 5, 6, 8 digits)
    - Verification URLs
    - Authentication tokens
    - Recovery codes
    - Google Authenticator codes
    - Codes with explicit keywords
    """
    
    def __init__(self, min_confidence: float = 0.3):
        """
        Initialize the code extractor.
        
        Args:
            min_confidence: Minimum confidence score for extracted codes (0.0-1.0)
        """
        self.min_confidence = min_confidence
        self.patterns = ALL_PATTERNS.copy()
    
    def extract_codes(
        self,
        text: str,
        patterns: Optional[List[str]] = None,
        include_context: bool = True,
        context_window: int = 50
    ) -> List[ExtractedCode]:
        """
        Extract codes from text using specified patterns.
        
        Args:
            text: Text to extract codes from
            patterns: List of pattern names to use (default: all patterns)
            include_context: Whether to include surrounding context
            context_window: Number of characters before/after the code for context
            
        Returns:
            List of ExtractedCode objects
        """
        if patterns is None:
            patterns = list(self.patterns.keys())
        
        extracted_codes = []
        
        for pattern_name in patterns:
            if pattern_name not in self.patterns:
                continue
            
            pattern = self.patterns[pattern_name]
            
            # Find all matches for this pattern
            for match in pattern.finditer(text):
                code = match.group()
                
                # Special handling for patterns with capture groups
                if pattern_name == 'google_auth' and match.groups():
                    code = match.group(1)  # Extract just the digits
                elif pattern_name == 'code_keyword' and match.groups():
                    code = match.group(1)  # Extract just the digits
                
                # Get context if requested
                context = ""
                if include_context:
                    start = max(0, match.start() - context_window)
                    end = min(len(text), match.end() + context_window)
                    context = text[start:end].strip()
                
                # Calculate confidence score
                confidence = calculate_confidence_score(code, pattern_name, context)
                
                # Skip if below minimum confidence
                if confidence < self.min_confidence:
                    continue
                
                # Create extracted code object
                extracted_code = ExtractedCode(
                    code=code,
                    code_type=pattern_name,
                    confidence=confidence,
                    context=context,
                    start_pos=match.start(),
                    end_pos=match.end()
                )
                
                extracted_codes.append(extracted_code)
        
        # Sort by confidence (highest first) and filter duplicates
        extracted_codes.sort(key=lambda x: (x.confidence, x.code_type), reverse=True)
        
        # Remove duplicate codes (same code and type) - keep highest confidence
        unique_codes = []
        seen_codes = {}
        
        for code in extracted_codes:
            key = code.code  # Only check the actual code, not type
            if key not in seen_codes:
                seen_codes[key] = code
                unique_codes.append(code)
            else:
                # Keep the one with higher confidence or prefer code_keyword type
                existing = seen_codes[key]
                if (code.confidence > existing.confidence or 
                    (code.confidence == existing.confidence and code.code_type == 'code_keyword')):
                    unique_codes.remove(existing)
                    unique_codes.append(code)
                    seen_codes[key] = code
        
        return unique_codes
    
    def extract_with_context(
        self,
        text: str,
        window: int = 50,
        patterns: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        """
        Extract codes with surrounding context.
        
        Args:
            text: Text to analyze
            window: Context window size in characters
            patterns: List of pattern names to use
            
        Returns:
            List of dictionaries with code info and context
        """
        codes = self.extract_codes(text, patterns, include_context=True, context_window=window)
        
        return [code.to_dict() for code in codes]
    
    def extract_from_html(
        self,
        html_content: str,
        patterns: Optional[List[str]] = None,
        preserve_formatting: bool = False
    ) -> List[ExtractedCode]:
        """
        Extract codes from HTML content.
        
        Args:
            html_content: HTML content to analyze
            patterns: List of pattern names to use
            preserve_formatting: Whether to preserve HTML formatting in context
            
        Returns:
            List of ExtractedCode objects
        """
        # Parse HTML
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Extract text from HTML
        if preserve_formatting:
            # Keep some formatting but make it readable
            text = soup.get_text(separator=' ', strip=True)
        else:
            # Clean text extraction
            text = soup.get_text(separator=' ', strip=True)
        
        # Also check specific HTML elements that might contain codes
        additional_texts = []
        
        # Check input values (common for verification codes)
        for input_tag in soup.find_all('input', {'value': True}):
            value = input_tag.get('value', '').strip()
            if value and re.search(r'\d', value):  # Contains at least one digit
                additional_texts.append(value)
        
        # Check code elements
        for code_tag in soup.find_all('code'):
            code_text = code_tag.get_text(strip=True)
            if code_text:
                additional_texts.append(code_text)
        
        # Check strong/bold tags (often used for codes)
        for strong_tag in soup.find_all(['strong', 'b']):
            strong_text = strong_tag.get_text(strip=True)
            if strong_text and re.search(r'\d', strong_text):
                additional_texts.append(strong_text)
        
        # Combine main text with additional elements
        combined_text = text + '\n' + '\n'.join(additional_texts)
        
        # Extract codes from combined text
        codes = self.extract_codes(combined_text, patterns)
        
        # Adjust positions to account for HTML elements if needed
        # (This is complex, so we'll skip for now)
        
        return codes
    
    def get_codes_by_type(
        self,
        text: str,
        code_type: str,
        min_confidence: Optional[float] = None
    ) -> List[ExtractedCode]:
        """
        Extract codes of a specific type.
        
        Args:
            text: Text to analyze
            code_type: Type of code to extract
            min_confidence: Override minimum confidence for this extraction
            
        Returns:
            List of ExtractedCode objects of the specified type
        """
        if min_confidence is None:
            min_confidence = self.min_confidence
        
        original_min_confidence = self.min_confidence
        self.min_confidence = min_confidence
        
        try:
            codes = self.extract_codes(text, patterns=[code_type])
        finally:
            self.min_confidence = original_min_confidence
        
        return codes
    
    def extract_otp_codes(self, text: str) -> List[ExtractedCode]:
        """Extract only OTP codes (4, 5, 6, 8 digits)."""
        otp_patterns = ['otp_4', 'otp_5', 'otp_6', 'otp_8', 'google_auth', 'code_keyword']
        return self.extract_codes(text, patterns=otp_patterns)
    
    def extract_urls(self, text: str) -> List[ExtractedCode]:
        """Extract only verification URLs."""
        return self.extract_codes(text, patterns=['verification_url'])
    
    def extract_tokens(self, text: str) -> List[ExtractedCode]:
        """Extract only authentication tokens."""
        return self.extract_codes(text, patterns=['token', 'recovery_code'])
    
    def get_pattern_description(self, pattern_name: str) -> str:
        """Get description for a pattern."""
        return PATTERN_DESCRIPTIONS.get(pattern_name, "Unknown pattern")
    
    def list_available_patterns(self) -> Dict[str, str]:
        """Get all available patterns and their descriptions."""
        return PATTERN_DESCRIPTIONS.copy()
    
    def set_min_confidence(self, confidence: float):
        """Update minimum confidence threshold."""
        self.min_confidence = max(0.0, min(1.0, confidence))
    
    def get_statistics(self, text: str) -> Dict[str, int]:
        """
        Get statistics about potential codes in text without extraction.
        
        Args:
            text: Text to analyze
            
        Returns:
            Dictionary with pattern name -> count of matches
        """
        stats = {}
        
        for pattern_name, pattern in self.patterns.items():
            matches = list(pattern.finditer(text))
            stats[pattern_name] = len(matches)
        
        return stats