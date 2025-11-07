"""
Unit tests for codes API endpoints.
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import Mock, patch
from datetime import datetime, timezone

from api.app import create_app
from core.database.models import EmailAccount, Message, ExtractedCode


class TestCodesAPI:
    """Test cases for codes API endpoints."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.app = create_app()
        self.client = TestClient(self.app)
        
        # Mock authentication - use correct header format
        self.auth_headers = {"X-API-Key": "dev_api_key"}
    
    @patch('api.auth.auth_required')
    def test_list_codes_for_email_no_codes(self, mock_auth):
        """Test listing codes when no codes exist."""
        mock_auth.return_value = {"sub": "test_user"}
        
        # Mock database responses
        with patch('core.database.operations.get_email_account_by_email') as mock_get_email, \
             patch('core.database.operations.get_extracted_codes_by_email') as mock_get_codes:
            
            # Mock email exists but no codes
            mock_email = Mock()
            mock_email.id = "email_123"
            mock_get_email.return_value = mock_email
            mock_get_codes.return_value = []
            
            response = self.client.get(
                "/codes/test@example.com",
                headers=self.auth_headers
            )
            
            assert response.status_code == 200
            data = response.json()
            assert data["email"] == "test@example.com"
            assert data["codes"] == []
            assert data["total"] == 0
    
    @patch('api.auth.auth_required')
    def test_list_codes_for_email_with_codes(self, mock_auth):
        """Test listing codes when codes exist."""
        mock_auth.return_value = {"sub": "test_user"}
        
        # Mock extracted codes
        mock_code = Mock()
        mock_code.id = "code_123"
        mock_code.code = "123456"
        mock_code.code_type = "otp_6"
        mock_code.confidence = 0.8
        mock_code.context = "Your code is 123456"
        mock_code.extracted_at = datetime.now(timezone.utc)
        mock_code.message_id = "msg_123"
        
        with patch('core.database.operations.get_email_account_by_email') as mock_get_email, \
             patch('core.database.operations.get_extracted_codes_by_email') as mock_get_codes:
            
            mock_email = Mock()
            mock_email.id = "email_123"
            mock_get_email.return_value = mock_email
            mock_get_codes.return_value = [mock_code]
            
            response = self.client.get(
                "/codes/test@example.com",
                headers=self.auth_headers
            )
            
            assert response.status_code == 200
            data = response.json()
            assert data["email"] == "test@example.com"
            assert len(data["codes"]) == 1
            assert data["codes"][0]["code"] == "123456"
            assert data["codes"][0]["type"] == "otp_6"
            assert data["codes"][0]["confidence"] == 0.8
            assert data["total"] == 1
    
    @patch('api.auth.auth_required')
    def test_list_codes_email_not_found(self, mock_auth):
        """Test listing codes for non-existent email."""
        mock_auth.return_value = {"sub": "test_user"}
        
        with patch('core.database.operations.get_email_account_by_email') as mock_get_email:
            mock_get_email.return_value = None
            
            response = self.client.get(
                "/codes/nonexistent@example.com",
                headers=self.auth_headers
            )
            
            assert response.status_code == 404
            assert "Email not found" in response.json()["detail"]
    
    @patch('api.auth.auth_required')
    def test_list_codes_with_type_filter(self, mock_auth):
        """Test listing codes filtered by type."""
        mock_auth.return_value = {"sub": "test_user"}
        
        with patch('core.database.operations.get_email_account_by_email') as mock_get_email, \
             patch('core.database.operations.get_extracted_codes_by_type') as mock_get_codes:
            
            mock_email = Mock()
            mock_email.id = "email_123"
            mock_get_email.return_value = mock_email
            mock_get_codes.return_value = []
            
            response = self.client.get(
                "/codes/test@example.com?type=otp_6",
                headers=self.auth_headers
            )
            
            assert response.status_code == 200
            mock_get_codes.assert_called_once()
            # Check that the filter was applied
            call_args = mock_get_codes.call_args
            assert call_args[1]["code_type"] == "otp_6"
    
    @patch('api.auth.auth_required')
    def test_list_codes_recent_filter(self, mock_auth):
        """Test listing only recent codes."""
        mock_auth.return_value = {"sub": "test_user"}
        
        with patch('core.database.operations.get_email_account_by_email') as mock_get_email, \
             patch('core.database.operations.get_recent_extracted_codes') as mock_get_codes:
            
            mock_email = Mock()
            mock_email.id = "email_123"
            mock_get_email.return_value = mock_email
            mock_get_codes.return_value = []
            
            response = self.client.get(
                "/codes/test@example.com?recent=true",
                headers=self.auth_headers
            )
            
            assert response.status_code == 200
            mock_get_codes.assert_called_once()
            # Check that recent filter was applied
            call_args = mock_get_codes.call_args
            assert call_args[1]["hours"] == 24
    
    @patch('api.auth.auth_required')
    def test_check_codes_no_messages(self, mock_auth):
        """Test checking codes when no messages exist."""
        mock_auth.return_value = {"sub": "test_user"}
        
        with patch('core.database.operations.get_email_account_by_email') as mock_get_email:
            mock_email = Mock()
            mock_email.id = "email_123"
            mock_get_email.return_value = mock_email
            
            with patch('core.database.session.get_session') as mock_session:
                mock_db = Mock()
                mock_session.return_value = mock_db
                mock_db.query.return_value.filter.return_value.all.return_value = []
                
                response = self.client.post(
                    "/codes/test@example.com/check",
                    json={},
                    headers=self.auth_headers
                )
                
                assert response.status_code == 200
                data = response.json()
                assert data["email"] == "test@example.com"
                assert data["processed_messages"] == 0
                assert data["new_codes_extracted"] == 0
                assert data["total_codes"] == 0
                assert data["codes"] == []
    
    @patch('api.auth.auth_required')
    def test_check_codes_with_extraction(self, mock_auth):
        """Test checking codes with successful extraction."""
        mock_auth.return_value = {"sub": "test_user"}
        
        # Mock message with content
        mock_message = Mock()
        mock_message.id = "msg_123"
        mock_message.full_text = "Your verification code is 123456"
        mock_message.text_preview = "Your verification code is 123456"
        mock_message.html_content = None
        
        with patch('core.database.operations.get_email_account_by_email') as mock_get_email:
            mock_email = Mock()
            mock_email.id = "email_123"
            mock_get_email.return_value = mock_email
            
            with patch('core.database.session.get_session') as mock_session:
                mock_db = Mock()
                mock_session.return_value = mock_db
                mock_db.query.return_value.filter.return_value.all.return_value = [mock_message]
                
                # Mock extraction operations
                with patch('core.database.operations.get_extracted_codes_by_message') as mock_existing, \
                     patch('core.database.operations.delete_extracted_codes_by_message') as mock_delete, \
                     patch('core.database.operations.bulk_add_extracted_codes') as mock_bulk_add, \
                     patch('core.database.operations.get_extracted_codes_by_email') as mock_get_all:
                    
                    mock_existing.return_value = []  # No existing codes
                    mock_delete.return_value = 0
                    mock_get_all.return_value = []
                    
                    response = self.client.post(
                        "/codes/test@example.com/check",
                        json={"force_refresh": True},
                        headers=self.auth_headers
                    )
                    
                    assert response.status_code == 200
                    data = response.json()
                    assert data["email"] == "test@example.com"
                    assert data["processed_messages"] == 1
                    assert data["new_codes_extracted"] > 0  # Should extract the code
                    mock_bulk_add.assert_called_once()
    
    @patch('api.auth.auth_required')
    def test_check_codes_with_patterns(self, mock_auth):
        """Test checking codes with specific patterns."""
        mock_auth.return_value = {"sub": "test_user"}
        
        mock_message = Mock()
        mock_message.id = "msg_123"
        mock_message.full_text = "Your verification code is 123456"
        mock_message.text_preview = "Your verification code is 123456"
        mock_message.html_content = None
        
        with patch('core.database.operations.get_email_account_by_email') as mock_get_email:
            mock_email = Mock()
            mock_email.id = "email_123"
            mock_get_email.return_value = mock_email
            
            with patch('core.database.session.get_session') as mock_session:
                mock_db = Mock()
                mock_session.return_value = mock_db
                mock_db.query.return_value.filter.return_value.all.return_value = [mock_message]
                
                with patch('core.database.operations.get_extracted_codes_by_message') as mock_existing, \
                     patch('core.database.operations.delete_extracted_codes_by_message') as mock_delete, \
                     patch('core.database.operations.bulk_add_extracted_codes') as mock_bulk_add, \
                     patch('core.database.operations.get_extracted_codes_by_email') as mock_get_all:
                    
                    mock_existing.return_value = []
                    mock_delete.return_value = 0
                    mock_get_all.return_value = []
                    
                    response = self.client.post(
                        "/codes/test@example.com/check",
                        json={"patterns": ["otp_6"]},
                        headers=self.auth_headers
                    )
                    
                    assert response.status_code == 200
                    # The extraction should be called with the specific pattern
                    mock_bulk_add.assert_called_once()
    
    @patch('api.auth.auth_required')
    def test_list_code_types(self, mock_auth):
        """Test listing available code types."""
        mock_auth.return_value = {"sub": "test_user"}
        
        with patch('core.database.operations.get_email_account_by_email') as mock_get_email, \
             patch('core.database.operations.get_extracted_codes_by_type') as mock_get_codes:
            
            mock_email = Mock()
            mock_email.id = "email_123"
            mock_get_email.return_value = mock_email
            mock_get_codes.return_value = []
            
            response = self.client.get(
                "/codes/test@example.com/types",
                headers=self.auth_headers
            )
            
            assert response.status_code == 200
            data = response.json()
            
            # Should contain all pattern types
            expected_types = [
                "otp_4", "otp_5", "otp_6", "otp_8",
                "verification_url", "token", "recovery_code",
                "google_auth", "code_keyword"
            ]
            
            for pattern_type in expected_types:
                assert pattern_type in data
                assert "description" in data[pattern_type]
                assert "count" in data[pattern_type]
    
    @patch('api.auth.auth_required')
    def test_delete_codes_all(self, mock_auth):
        """Test deleting all codes for an email."""
        mock_auth.return_value = {"sub": "test_user"}
        
        # Mock codes to delete
        mock_code = Mock()
        
        with patch('core.database.operations.get_email_account_by_email') as mock_get_email, \
             patch('core.database.operations.get_extracted_codes_by_email') as mock_get_codes:
            
            mock_email = Mock()
            mock_email.id = "email_123"
            mock_get_email.return_value = mock_email
            mock_get_codes.return_value = [mock_code]
            
            with patch('core.database.session.get_session') as mock_session:
                mock_db = Mock()
                mock_session.return_value = mock_db
                
                response = self.client.delete(
                    "/codes/test@example.com",
                    headers=self.auth_headers
                )
                
                assert response.status_code == 200
                data = response.json()
                assert data["email"] == "test@example.com"
                assert data["deleted_count"] == 1
                assert data["type_filter"] is None
    
    @patch('api.auth.auth_required')
    def test_delete_codes_by_type(self, mock_auth):
        """Test deleting codes of specific type."""
        mock_auth.return_value = {"sub": "test_user"}
        
        mock_code = Mock()
        
        with patch('core.database.operations.get_email_account_by_email') as mock_get_email, \
             patch('core.database.operations.get_extracted_codes_by_type') as mock_get_codes:
            
            mock_email = Mock()
            mock_email.id = "email_123"
            mock_get_email.return_value = mock_email
            mock_get_codes.return_value = [mock_code]
            
            with patch('core.database.session.get_session') as mock_session:
                mock_db = Mock()
                mock_session.return_value = mock_db
                
                response = self.client.delete(
                    "/codes/test@example.com?type=otp_6",
                    headers=self.auth_headers
                )
                
                assert response.status_code == 200
                data = response.json()
                assert data["email"] == "test@example.com"
                assert data["deleted_count"] == 1
                assert data["type_filter"] == "otp_6"
                # Check that the filter was applied
                mock_get_codes.assert_called_once_with(
                    db=mock_db, 
                    email_id="email_123", 
                    code_type="otp_6"
                )
    
    @patch('api.auth.auth_required')
    def test_delete_codes_email_not_found(self, mock_auth):
        """Test deleting codes for non-existent email."""
        mock_auth.return_value = {"sub": "test_user"}
        
        with patch('core.database.operations.get_email_account_by_email') as mock_get_email:
            mock_get_email.return_value = None
            
            response = self.client.delete(
                "/codes/nonexistent@example.com",
                headers=self.auth_headers
            )
            
            assert response.status_code == 404
            assert "Email not found" in response.json()["detail"]
    
    def test_codes_endpoints_require_auth(self):
        """Test that all codes endpoints require authentication."""
        endpoints = [
            ("/codes/test@example.com", "GET"),
            ("/codes/test@example.com/check", "POST"),
            ("/codes/test@example.com/types", "GET"),
            ("/codes/test@example.com", "DELETE"),
        ]
        
        for endpoint, method in endpoints:
            response = self.client.request(method, endpoint)
            assert response.status_code == 403 or response.status_code == 401


if __name__ == "__main__":
    pytest.main([__file__])