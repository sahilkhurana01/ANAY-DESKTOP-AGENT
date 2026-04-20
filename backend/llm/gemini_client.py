import google.generativeai as genai
from typing import List, Dict, Optional
import logging
import asyncio

logger = logging.getLogger(__name__)

class GeminiClient:
    """Handles interactions with Google Gemini API."""
    
    def __init__(self, api_key: str, model_name: str = "gemini-1.5-flash"):
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel(model_name)
        self.chat_history = []
        self.system_prompt = "You are ANAY, a confident, calm, and intelligent AI assistant. Respond exclusively in English. Keep responses concise for voice interaction."

    def add_to_history(self, role: str, content: str):
        self.chat_history.append({"role": role, "parts": [content]})
        if len(self.chat_history) > 20:
            self.chat_history = self.chat_history[-20:]

    async def generate_response(self, text: str) -> str:
        """Generate response from Gemini."""
        try:
            # Simple chat session
            chat = self.model.start_chat(history=self.chat_history)
            
            # Prepend system prompt if history is empty or periodically? 
            # Better to use System Instructions if supported by SDK version, or just include in first message.
            if not self.chat_history:
                text = f"{self.system_prompt}\n\nUser: {text}"
            
            response = await asyncio.to_thread(chat.send_message, text)
            ai_text = response.text
            
            self.add_to_history("user", text)
            self.add_to_history("model", ai_text)
            
            return ai_text
            
        except Exception as e:
            logger.error(f"Gemini Error: {e}")
            return "I'm sorry, I'm having trouble understanding that. Could you please repeat?"
