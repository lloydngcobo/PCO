"""
Ollama Client Module
Handles communication with Ollama API for AI-powered responses
"""

import os
import requests
from typing import Dict, Any, Optional, List
from dotenv import load_dotenv

load_dotenv()


class OllamaClient:
    """Client for interacting with Ollama API"""
    
    def __init__(self, 
                 api_url: Optional[str] = None,
                 model: Optional[str] = None,
                 timeout: int = 120):
        """
        Initialize Ollama client.
        
        Args:
            api_url: Ollama API URL (default: from env or localhost:11434)
            model: Model to use (default: from env or llama3.1:8b)
            timeout: Request timeout in seconds
        """
        self.api_url = api_url or os.getenv("OLLAMA_API_URL", "http://localhost:11434/api/generate")
        self.model = model or os.getenv("OLLAMA_MODEL", "llama3.1:8b")
        self.timeout = timeout
        self.chat_url = self.api_url.replace("/generate", "/chat")
        
    def generate(self, 
                 prompt: str, 
                 system_prompt: Optional[str] = None,
                 temperature: float = 0.7,
                 stream: bool = False) -> str:
        """
        Generate a response from Ollama.
        
        Args:
            prompt: The user prompt
            system_prompt: Optional system prompt for context
            temperature: Sampling temperature (0.0 to 1.0)
            stream: Whether to stream the response
            
        Returns:
            Generated response text
            
        Raises:
            Exception: If API request fails
        """
        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": stream,
            "options": {
                "temperature": temperature
            }
        }
        
        if system_prompt:
            payload["system"] = system_prompt
        
        try:
            response = requests.post(
                self.api_url,
                json=payload,
                timeout=self.timeout
            )
            response.raise_for_status()
            
            if stream:
                return response.text
            else:
                return response.json().get("response", "")
                
        except requests.exceptions.RequestException as e:
            raise Exception(f"Ollama API error: {str(e)}")
    
    def chat(self,
             messages: List[Dict[str, str]],
             temperature: float = 0.7,
             stream: bool = False) -> str:
        """
        Have a chat conversation with Ollama.
        
        Args:
            messages: List of message dicts with 'role' and 'content'
            temperature: Sampling temperature (0.0 to 1.0)
            stream: Whether to stream the response
            
        Returns:
            Generated response text
            
        Example:
            >>> messages = [
            ...     {"role": "system", "content": "You are a helpful assistant."},
            ...     {"role": "user", "content": "Hello!"}
            ... ]
            >>> response = client.chat(messages)
        """
        payload = {
            "model": self.model,
            "messages": messages,
            "stream": stream,
            "options": {
                "temperature": temperature
            }
        }
        
        try:
            response = requests.post(
                self.chat_url,
                json=payload,
                timeout=self.timeout
            )
            response.raise_for_status()
            
            if stream:
                return response.text
            else:
                result = response.json()
                return result.get("message", {}).get("content", "")
                
        except requests.exceptions.RequestException as e:
            raise Exception(f"Ollama chat API error: {str(e)}")
    
    def check_health(self) -> bool:
        """
        Check if Ollama service is available.
        
        Returns:
            True if service is healthy, False otherwise
        """
        try:
            # Try to get the list of models
            tags_url = self.api_url.replace("/api/generate", "/api/tags")
            response = requests.get(tags_url, timeout=5)
            return response.status_code == 200
        except:
            return False
    
    def list_models(self) -> List[str]:
        """
        List available models in Ollama.
        
        Returns:
            List of model names
        """
        try:
            tags_url = self.api_url.replace("/api/generate", "/api/tags")
            response = requests.get(tags_url, timeout=5)
            response.raise_for_status()
            
            models = response.json().get("models", [])
            return [model.get("name") for model in models]
        except:
            return []


# Singleton instance
_ollama_client = None


def get_ollama_client() -> OllamaClient:
    """
    Get or create singleton Ollama client instance.
    
    Returns:
        OllamaClient instance
    """
    global _ollama_client
    if _ollama_client is None:
        _ollama_client = OllamaClient()
    return _ollama_client