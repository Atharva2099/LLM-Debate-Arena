"""
LLM Debate Arena - LLM API Service
This module handles the communication with various LLM APIs through OpenRouter
"""

import os
import requests
import logging
import json
from typing import Dict, Any, Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# OpenRouter API endpoint
OPENROUTER_API_ENDPOINT = "https://openrouter.ai/api/v1/chat/completions"

# Model identifiers on OpenRouter - updated with valid model IDs from documentation
OPENROUTER_MODELS = {
    "phi4": "microsoft/phi-4",
    "gemini": "google/gemini-2.5-flash-preview",
    "qwen": "qwen/qwen3-14b"
}

class LLMApiService:
    """Service for interacting with various LLM APIs through OpenRouter"""
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the LLM API service
        
        Args:
            api_key: OpenRouter API key
        """
        self.api_key = api_key or os.getenv("OPENROUTER_API_KEY", "")
        
        # App info for OpenRouter request headers
        self.app_name = "LLM Debate Arena"
        self.app_version = "1.0.0"
        
        # Log API key status
        if not self.api_key:
            logger.warning("No OpenRouter API key found. Set the OPENROUTER_API_KEY environment variable.")
        else:
            logger.info("OpenRouter API key found. Ready to make API calls.")
    
    def update_api_keys(self, api_keys: Dict[str, str]) -> None:
        """
        Update the API key
        
        Args:
            api_keys: Dictionary of API keys (will use 'openrouter' key)
        """
        if 'openrouter' in api_keys:
            self.api_key = api_keys['openrouter']
            logger.info("OpenRouter API key updated.")
    
    def generate_response(self, model_id: str, prompt: str, 
                         max_tokens: int = 250, temperature: float = 0.7) -> str:
        """
        Generate a response from an LLM through OpenRouter
        
        Args:
            model_id: ID of the model to use (phi4, gemini, qwen)
            prompt: Prompt to send to the model
            max_tokens: Maximum number of tokens to generate
            temperature: Temperature for generation
            
        Returns:
            Generated response string
        """
        logger.info(f"Generating response from {model_id} model")
        
        if not self.api_key:
            error_msg = "No OpenRouter API key found. Set the OPENROUTER_API_KEY environment variable."
            logger.error(error_msg)
            return f"Error: {error_msg}"
        
        # Get the full model identifier for OpenRouter
        openrouter_model = OPENROUTER_MODELS.get(model_id)
        if not openrouter_model:
            error_msg = f"Unsupported model ID: {model_id}"
            logger.error(error_msg)
            return f"Error: {error_msg}"
        
        try:
            return self._call_openrouter_api(openrouter_model, prompt, max_tokens, temperature)
        except Exception as e:
            error_msg = f"Error generating response from {model_id} via OpenRouter: {str(e)}"
            logger.error(error_msg)
            return f"Error: {error_msg}"
    
    def _call_openrouter_api(self, model: str, prompt: str, 
                           max_tokens: int, temperature: float) -> str:
        """
        Call the OpenRouter API
        
        Args:
            model: Full model identifier for OpenRouter
            prompt: Prompt to send to the model
            max_tokens: Maximum number of tokens to generate
            temperature: Temperature for generation
            
        Returns:
            Generated response string
        """
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}",
            "HTTP-Referer": "https://llm-debate-arena.example.com",  # Replace with your actual domain
            "X-Title": "LLM Debate Arena",
        }
        
        data = {
            "model": model,
            "messages": [
                {"role": "system", "content": "You are a helpful AI assistant participating in a debate."},
                {"role": "user", "content": prompt}
            ],
            "max_tokens": max_tokens,
            "temperature": temperature
        }
        
        logger.info(f"Making API call to OpenRouter for model: {model}")
        
        response = requests.post(
            OPENROUTER_API_ENDPOINT,
            headers=headers,
            json=data,
            timeout=30
        )
        
        if response.status_code != 200:
            error_msg = f"OpenRouter API error ({response.status_code}): {response.text}"
            logger.error(error_msg)
            return f"Error: {error_msg}"
        
        # Parse the response
        response_data = response.json()
        try:
            message = response_data["choices"][0]["message"]["content"]
            logger.info(f"Successfully generated response ({len(message)} chars)")
            return message
        except (KeyError, IndexError) as e:
            logger.error(f"Error parsing OpenRouter response: {str(e)}")
            return "No response text found in the OpenRouter API response"


# For testing the API service
if __name__ == "__main__":
    # Create a test API service
    api_service = LLMApiService()
    
    # Check if API key is set
    if not api_service.api_key:
        logger.warning("No OpenRouter API key found. Please set the OPENROUTER_API_KEY environment variable.")
        exit(1)
    
    # Test the API service with a sample prompt
    logger.info("Testing OpenRouter API with a sample prompt...")
    test_prompt = "Write a short sentence about artificial intelligence."
    model_id = "phi4"  # Test with Phi-4
    
    response = api_service.generate_response(model_id, test_prompt)
    logger.info(f"Response from {model_id}: {response}")