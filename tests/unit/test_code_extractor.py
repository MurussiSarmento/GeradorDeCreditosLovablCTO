"""
Unit tests for code extraction functionality.
"""

import pytest
from datetime import datetime, timezone
from core.extraction import CodeExtractor
from core.extraction.patterns import ALL_PATTERNS
from core.extraction.validators import (
    is_likely_otp,
    is_likely_url,
    is_likely_token,
    calculate_confidence_score
)


class TestCodeExtractor:
    """Test cases for CodeExtractor class."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.extractor = CodeExtractor(min_confidence=0.3)
    
    def test_extract_otp_codes(self):
        """Test extraction of OTP codes."""
        text = "Your verification code is 123456. Please use it within 10 minutes."
        codes = self.extractor.extract_otp_codes(text)
        
        assert len(codes) > 0
        assert any(code.code == "123456" for code in codes)
        assert any(code.code_type in ["otp_6", "code_keyword"] for code in codes)
    
    def test_extract_4_digit_code(self):
        """Test extraction of 4-digit codes."""
        text = "Your PIN is 4321. Keep it safe."
        codes = self.extractor.extract_codes(text, patterns=["otp_4"])
        
        assert len(codes) == 1
        assert codes[0].code == "4321"
        assert codes[0].code_type == "otp_4"
    
    def test_extract_6_digit_code(self):
        """Test extraction of 6-digit codes."""
        text = "Enter code 789012 to continue."
        codes = self.extractor.extract_codes(text, patterns=["otp_6"])
        
        assert len(codes) == 1
        assert codes[0].code == "789012"
        assert codes[0].code_type == "otp_6"
    
    def test_extract_verification_urls(self):
        """Test extraction of verification URLs."""
        text = "Please verify your account: https://example.com/verify?token=abc123"
        codes = self.extractor.extract_urls(text)
        
        assert len(codes) == 1
        assert "verify" in codes[0].code.lower()
        assert codes[0].code_type == "verification_url"
    
    def test_extract_google_auth_code(self):
        """Test extraction of Google Authenticator codes."""
        text = "Your Google Authenticator code is 654321 for account verification."
        codes = self.extractor.extract_codes(text, patterns=["google_auth"])
        
        assert len(codes) == 1
        assert codes[0].code == "654321"
        assert codes[0].code_type == "google_auth"
    
    def test_extract_code_with_keyword(self):
        """Test extraction of codes with explicit keywords."""
        text = "Code: 987654 is your verification code."
        codes = self.extractor.extract_codes(text, patterns=["code_keyword"])
        
        assert len(codes) == 1
        assert codes[0].code == "987654"
        assert codes[0].code_type == "code_keyword"
    
    def test_extract_recovery_codes(self):
        """Test extraction of recovery codes."""
        text = "Your recovery codes are: AB12-CD34-EF56 and GH78-IJ90-KL12"
        codes = self.extractor.extract_codes(text, patterns=["recovery_code"])
        
        assert len(codes) >= 1
        assert any("AB12" in code.code for code in codes)
        assert codes[0].code_type == "recovery_code"
    
    def test_extract_from_html(self):
        """Test extraction from HTML content."""
        html = """
        <html>
            <body>
                <p>Your code is: <strong>123456</strong></p>
                <input type="text" value="789012" />
                <code>ABC123</code>
            </body>
        </html>
        """
        codes = self.extractor.extract_from_html(html)
        
        # Should extract codes from various HTML elements
        assert len(codes) >= 2
        assert any(code.code == "123456" for code in codes)
        assert any(code.code == "789012" for code in codes)
    
    def test_confidence_filtering(self):
        """Test that low confidence codes are filtered out."""
        text = "Random numbers: 111111, 222222, 123456"
        extractor = CodeExtractor(min_confidence=0.8)  # High threshold
        codes = extractor.extract_codes(text)
        
        # Should filter out obvious patterns like 111111, 222222
        high_conf_codes = [c for c in codes if c.confidence >= 0.8]
        assert any(code.code == "123456" for code in high_conf_codes)
    
    def test_context_extraction(self):
        """Test context extraction around codes."""
        text = "Please enter verification code 456789 within 5 minutes."
        codes = self.extractor.extract_with_context(text, window=10)
        
        assert len(codes) > 0
        code = codes[0]
        assert code["code"] == "456789"
        assert "verification" in code["context"].lower()
        assert "minutes" in code["context"].lower()
    
    def test_duplicate_removal(self):
        """Test that duplicate codes are removed."""
        text = "Code: 123456. Again: 123456. One more time: 123456."
        codes = self.extractor.extract_codes(text)
        
        # Should only have one instance of 123456
        code_123456 = [c for c in codes if c.code == "123456"]
        assert len(code_123456) == 1
    
    def test_get_codes_by_type(self):
        """Test filtering codes by type."""
        text = "OTP: 123456. URL: https://verify.example.com"
        otp_codes = self.extractor.get_codes_by_type(text, "otp_6")
        url_codes = self.extractor.get_codes_by_type(text, "verification_url")
        
        assert len(otp_codes) == 1
        assert otp_codes[0].code == "123456"
        assert len(url_codes) == 1
        assert "verify" in url_codes[0].code.lower()
        assert "verify" in url_codes[0].code.lower()
    
    def test_pattern_descriptions(self):
        """Test pattern descriptions are available."""
        descriptions = self.extractor.list_available_patterns()
        
        assert isinstance(descriptions, dict)
        assert "otp_6" in descriptions
        assert "verification_url" in descriptions
        assert len(descriptions["otp_6"]) > 0
    
    def test_statistics(self):
        """Test statistics calculation."""
        text = "Codes: 1234, 56789, https://verify.com, ABC123DEF456"
        stats = self.extractor.get_statistics(text)
        
        assert isinstance(stats, dict)
        assert "otp_4" in stats
        assert "otp_5" in stats
        assert "verification_url" in stats
        assert "token" in stats
        assert stats["otp_4"] >= 1
        assert stats["otp_5"] >= 1


class TestCodeValidators:
    """Test cases for code validation functions."""
    
    def test_is_likely_otp_valid(self):
        """Test OTP validation with valid codes."""
        assert is_likely_otp("123456")
        assert is_likely_otp("7890")
        assert is_likely_otp("12345678")
    
    def test_is_likely_otp_invalid(self):
        """Test OTP validation with invalid codes."""
        assert not is_likely_otp("111111")  # Repeating
        assert not is_likely_otp("123456")  # Sequential (should be filtered)
        assert not is_likely_otp("123")  # Too short
        assert not is_likely_otp("123456789")  # Too long
        assert not is_likely_otp("abcdef")  # No digits
    
    def test_is_likely_url_valid(self):
        """Test URL validation with valid URLs."""
        assert is_likely_url("https://example.com/verify")
        assert is_likely_url("https://app.example.com/auth/confirm")
        assert is_likely_url("http://test.com/activate")
    
    def test_is_likely_url_invalid(self):
        """Test URL validation with invalid URLs."""
        assert not is_likely_url("https://example.com")  # No verification keyword
        assert not is_likely_url("ftp://example.com/verify")  # Not HTTP/HTTPS
        assert not is_likely_url("just some text")
    
    def test_is_likely_token_valid(self):
        """Test token validation with valid tokens."""
        assert is_likely_token("ABC123DEF456")
        assert is_likely_token("a1b2c3d4e5f6")
        assert is_likely_token("TOKEN123")
    
    def test_is_likely_token_invalid(self):
        """Test token validation with invalid tokens."""
        assert not is_likely_token("test")  # Common word
        assert not is_likely_token("12345678")  # Only numbers, too short
        assert not is_likely_token("a")  # Too short
        assert not is_likely_token("ABCDEFGHIJKLMNOPQRSTUVWXYZ")  # Too long
    
    def test_calculate_confidence_score(self):
        """Test confidence score calculation."""
        # High confidence for codes with keywords
        score1 = calculate_confidence_score("123456", "code_keyword", "Your code is: 123456")
        assert score1 > 0.7
        
        # Medium confidence for regular OTP
        score2 = calculate_confidence_score("123456", "otp_6", "Enter 123456")
        assert score2 > 0.5
        
        # Lower confidence for generic tokens
        score3 = calculate_confidence_score("ABC123", "token", "Token: ABC123")
        assert score3 < score1


class TestExtractedCode:
    """Test cases for ExtractedCode class."""
    
    def test_extracted_code_creation(self):
        """Test ExtractedCode object creation."""
        code = ExtractedCode(
            code="123456",
            code_type="otp_6",
            confidence=0.8,
            context="Your code is 123456",
            start_pos=15,
            end_pos=21
        )
        
        assert code.code == "123456"
        assert code.code_type == "otp_6"
        assert code.confidence == 0.8
        assert code.context == "Your code is 123456"
        assert code.start_pos == 15
        assert code.end_pos == 21
    
    def test_extracted_code_to_dict(self):
        """Test ExtractedCode to_dict conversion."""
        code = ExtractedCode(
            code="123456",
            code_type="otp_6",
            confidence=0.8
        )
        
        code_dict = code.to_dict()
        
        assert isinstance(code_dict, dict)
        assert code_dict["code"] == "123456"
        assert code_dict["type"] == "otp_6"
        assert code_dict["confidence"] == 0.8
        assert "context" in code_dict
        assert "start_pos" in code_dict
        assert "end_pos" in code_dict
    
    def test_extracted_code_repr(self):
        """Test ExtractedCode string representation."""
        from core.extraction.code_extractor import ExtractedCode
        
        code = ExtractedCode(
            code="123456",
            code_type="otp_6",
            confidence=0.8
        )
        
        repr_str = repr(code)
        assert "ExtractedCode" in repr_str
        assert "123456" in repr_str
        assert "otp_6" in repr_str
        assert "0.80" in repr_str


class TestPatternConstants:
    """Test pattern constants."""
    
    def test_all_patterns_exist(self):
        """Test that all expected patterns are defined."""
        expected_patterns = [
            "otp_4", "otp_5", "otp_6", "otp_8",
            "verification_url", "token", "recovery_code",
            "google_auth", "code_keyword"
        ]
        
        for pattern in expected_patterns:
            assert pattern in ALL_PATTERNS
            assert ALL_PATTERNS[pattern] is not None
    
    def test_patterns_are_compiled(self):
        """Test that all patterns are compiled regex objects."""
        import re
        
        for pattern_name, pattern in ALL_PATTERNS.items():
            assert isinstance(pattern, re.Pattern)
            assert hasattr(pattern, 'search')
            assert hasattr(pattern, 'findall')


if __name__ == "__main__":
    pytest.main([__file__])