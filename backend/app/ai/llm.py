import time
from typing import List, Dict, Any
import groq
from app.ai.interfaces import LLMProvider
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)

class GroqProvider(LLMProvider):
    def __init__(self):
        self.client = groq.Groq(api_key=settings.GROQ_API_KEY)
        self.model = "llama-3.1-8b-instant" # Updated from decommissioned llama3-8b-8192

    def generate_response(self, system_prompt: str, messages: List[Dict[str, str]], **kwargs) -> Dict[str, Any]:
        start_time = time.time()
        
        # We need to enforce JSON output as requested
        # Groq supports JSON mode if the prompt specifies it.
        
        formatted_messages = [{"role": "system", "content": system_prompt}] + messages
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=formatted_messages,
                response_format={"type": "json_object"},
                temperature=0.0, # strict, no hallucination
                max_tokens=2048,
                **kwargs
            )
            
            end_time = time.time()
            
            return {
                "content": response.choices[0].message.content,
                "prompt_tokens": response.usage.prompt_tokens,
                "completion_tokens": response.usage.completion_tokens,
                "response_time_ms": (end_time - start_time) * 1000
            }
        except Exception as e:
            logger.error(f"Groq API Error: {str(e)}")
            raise e

llm_provider = GroqProvider()
