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

# Model identifiers on OpenRouter
OPENROUTER_MODELS = {
    "phi4": "microsoft/phi-3-mini",
    "gemini": "google/gemini-pro",
    "qwen": "qwen/qwen1.5-14b-chat"
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
    
    def update_api_keys(self, api_keys: Dict[str, str]) -> None:
        """
        Update the API key
        
        Args:
            api_keys: Dictionary of API keys (will use 'openrouter' key)
        """
        if 'openrouter' in api_keys:
            self.api_key = api_keys['openrouter']
    
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
        if not self.api_key:
            error_msg = "No OpenRouter API key found"
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
            "X-Title": self.app_name,
            "X-Version": self.app_version
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
            return response_data["choices"][0]["message"]["content"]
        except (KeyError, IndexError) as e:
            logger.error(f"Error parsing OpenRouter response: {str(e)}")
            return "No response text found in the OpenRouter API response"

    def handle_debater_prompt(self, debate_data: Dict[str, Any], debater_index: int) -> str:
        """
        Generate a debate response based on the current debate state
        
        Args:
            debate_data: Current debate data
            debater_index: Index of the debater in the debate data
            
        Returns:
            Generated debate response
        """
        try:
            # Extract debate information
            topic = debate_data.get("topic", "")
            round_num = debate_data.get("round", 1)
            exchange_num = debate_data.get("exchange", 0)
            
            # Get debater information
            debater = debate_data["debaters"][debater_index]
            model_id = debater.get("id", "")
            position = debater.get("position", "pro")
            codename = debater.get("codename", "")
            
            # Get opponent's last message if applicable
            opponent_message = None
            if exchange_num > 0 or (exchange_num == 0 and round_num > 1):
                # Find the last message from the opponent
                for msg in reversed(debate_data.get("debate_log", [])):
                    if msg.get("type") == "debater" and msg.get("debater") != codename:
                        opponent_message = msg.get("content", "")
                        break
            
            # Construct prompt based on debate phase
            if exchange_num == 0:
                # Opening statement
                prompt = (
                    f"You are participating in a structured debate on the topic: '{topic}'. "
                    f"You have been assigned the {position} position. "
                    f"Make your opening argument in 150 words or less. "
                    f"Focus on making a compelling, logical case supported by evidence where appropriate. "
                    f"Identify yourself as {codename}."
                )
            elif exchange_num == 9:  # Last exchange in a round (based on EXCHANGES_PER_ROUND = 10)
                # Conclusion statement
                prompt = (
                    f"You are participating in a structured debate on the topic: '{topic}'. "
                    f"You have been assigned the {position} position. "
                    f"This is your concluding statement. Summarize your main arguments and address the "
                    f"key points from your opponent's position in 200 words or less. "
                    f"Make your final case compelling and memorable. "
                    f"Identify yourself as {codename}."
                )
            else:
                # Regular exchange
                opponent_codename = None
                for d in debate_data["debaters"]:
                    if d != debater:
                        opponent_codename = d.get("codename", "Opponent")
                        break
                
                prompt = (
                    f"You are participating in a structured debate on the topic: '{topic}'. "
                    f"You have been assigned the {position} position. "
                    f"Your opponent, {opponent_codename}, just made the following argument:\n\n"
                    f"\"{opponent_message}\"\n\n"
                    f"Respond to their argument in 150 words or less. "
                    f"Make your argument compelling and logical, addressing their points directly. "
                    f"Identify yourself as {codename}."
                )
            
            # Generate response
            return self.generate_response(
                model_id=model_id,
                prompt=prompt,
                max_tokens=300,  # Adjust based on word limits (approximately 4 tokens per word)
                temperature=0.7
            )
        
        except Exception as e:
            error_msg = f"Error generating debate response: {str(e)}"
            logger.error(error_msg)
            return f"Error: {error_msg}"


# For testing the API service
if __name__ == "__main__":
    # Create a test API service
    api_service = LLMApiService()
    
    # Check if API key is set
    if not api_service.api_key:
        print("Warning: No OpenRouter API key found. Please set the OPENROUTER_API_KEY environment variable.")
        exit(1)
    
    # Test each model with a sample prompt
    test_prompt = "Write a short sentence about artificial intelligence."
    
    for model_id in OPENROUTER_MODELS.keys():
        print(f"\nTesting {model_id} via OpenRouter...")
        response = api_service.generate_response(model_id, test_prompt)
        print(f"Response: {response}")