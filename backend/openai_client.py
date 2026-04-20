"""
OpenAI API Client
Handles AI conversation using OpenAI API
"""
import os
import logging
import openai
from typing import List, Dict, Optional
from config import OPENAI_API_KEY, OPENAI_MODEL, DEFAULT_TEMPERATURE, DEFAULT_MAX_TOKENS

logger = logging.getLogger(__name__)

class OpenAIClient:
    """Client for OpenAI API to generate conversational responses."""
    
    def __init__(self, api_key: str = None, model: str = None):
        """
        Initialize OpenAI client.
        
        Args:
            api_key: OpenAI API key (defaults to config)
            model: Model to use (defaults to config)
        """
        self.api_key = api_key or OPENAI_API_KEY
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY not found. Please set it in config or environment.")
        
        self.model = model or OPENAI_MODEL
        self.client = openai.OpenAI(api_key=self.api_key)
        self.conversation_history: List[Dict[str, str]] = []
        
        logger.info(f"OpenAI client initialized with model: {self.model}")
    
    def generate_response(
        self,
        user_message: str,
        temperature: float = None,
        max_tokens: int = None,
        system_prompt: str = None
    ) -> str:
        """
        Generate AI response to user message.
        
        Args:
            user_message: User's input message
            temperature: Response creativity (0.0-2.0)
            max_tokens: Maximum tokens in response
            system_prompt: System prompt for AI behavior
            
        Returns:
            AI generated response text
        """
        try:
            # Build messages list
            messages = []
            
            # Add system prompt if provided
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            elif not self.conversation_history:
                # Default system prompt for first message
                messages.append({
                    "role": "system",
                    "content": "You are ANAY, a helpful and friendly AI assistant. Be conversational, concise, and helpful."
                })
            
            # Add conversation history
            messages.extend(self.conversation_history[-10:])  # Keep last 10 exchanges
            
            # Add current user message
            messages.append({"role": "user", "content": user_message})
            
            logger.info(f"Generating response for: {user_message[:50]}...")
            
            # Call OpenAI API
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=temperature or DEFAULT_TEMPERATURE,
                max_tokens=max_tokens or DEFAULT_MAX_TOKENS
            )
            
            # Extract response text
            ai_response = response.choices[0].message.content.strip()
            
            # Update conversation history
            self.conversation_history.append({"role": "user", "content": user_message})
            self.conversation_history.append({"role": "assistant", "content": ai_response})
            
            # Keep history manageable (last 20 messages)
            if len(self.conversation_history) > 20:
                self.conversation_history = self.conversation_history[-20:]
            
            logger.info(f"Response generated: {ai_response[:50]}...")
            return ai_response
            
        except Exception as e:
            logger.error(f"OpenAI API error: {e}")
            raise
    
    def clear_history(self):
        """Clear conversation history."""
        self.conversation_history = []
        logger.info("Conversation history cleared")
    
    def set_system_prompt(self, prompt: str):
        """Set a custom system prompt (will be used in next conversation)."""
        # Clear history and set new system prompt
        self.conversation_history = []
        if self.conversation_history:
            self.conversation_history[0] = {"role": "system", "content": prompt}
        logger.info("System prompt updated")


if __name__ == "__main__":
    # Test OpenAI client
    logging.basicConfig(level=logging.INFO)
    
    try:
        client = OpenAIClient()
        response = client.generate_response("Hello! Can you introduce yourself?")
        print(f"AI Response: {response}")
    except Exception as e:
        print(f"Error: {e}")
