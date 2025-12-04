"""
Tests for Ollama Client
"""

import pytest
from unittest.mock import Mock, patch
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from ollama_client import OllamaClient


class TestOllamaClient:
    """Test cases for OllamaClient"""
    
    def test_init_default(self):
        """Test client initialization with defaults"""
        client = OllamaClient()
        assert client.api_url is not None
        assert client.model is not None
        assert client.timeout == 120
    
    def test_init_custom(self):
        """Test client initialization with custom values"""
        client = OllamaClient(
            api_url="http://custom:11434/api/generate",
            model="custom-model",
            timeout=60
        )
        assert client.api_url == "http://custom:11434/api/generate"
        assert client.model == "custom-model"
        assert client.timeout == 60
    
    @patch('ollama_client.requests.post')
    def test_generate_success(self, mock_post):
        """Test successful generation"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"response": "Test response"}
        mock_post.return_value = mock_response
        
        client = OllamaClient()
        response = client.generate("Test prompt")
        
        assert response == "Test response"
        mock_post.assert_called_once()
    
    @patch('ollama_client.requests.post')
    def test_generate_with_system_prompt(self, mock_post):
        """Test generation with system prompt"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"response": "Test response"}
        mock_post.return_value = mock_response
        
        client = OllamaClient()
        response = client.generate("Test prompt", system_prompt="System prompt")
        
        assert response == "Test response"
        call_args = mock_post.call_args
        assert call_args[1]['json']['system'] == "System prompt"
    
    @patch('ollama_client.requests.post')
    def test_chat_success(self, mock_post):
        """Test successful chat"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "message": {"content": "Chat response"}
        }
        mock_post.return_value = mock_response
        
        client = OllamaClient()
        messages = [
            {"role": "user", "content": "Hello"}
        ]
        response = client.chat(messages)
        
        assert response == "Chat response"
        mock_post.assert_called_once()
    
    @patch('ollama_client.requests.get')
    def test_check_health_success(self, mock_get):
        """Test health check success"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_get.return_value = mock_response
        
        client = OllamaClient()
        is_healthy = client.check_health()
        
        assert is_healthy is True
    
    @patch('ollama_client.requests.get')
    def test_check_health_failure(self, mock_get):
        """Test health check failure"""
        mock_get.side_effect = Exception("Connection error")
        
        client = OllamaClient()
        is_healthy = client.check_health()
        
        assert is_healthy is False
    
    @patch('ollama_client.requests.get')
    def test_list_models_success(self, mock_get):
        """Test listing models"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "models": [
                {"name": "model1"},
                {"name": "model2"}
            ]
        }
        mock_get.return_value = mock_response
        
        client = OllamaClient()
        models = client.list_models()
        
        assert len(models) == 2
        assert "model1" in models
        assert "model2" in models