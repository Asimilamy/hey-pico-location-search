"""
OpenWebUI LLM integration module
Handles communication with local LLM
"""
import asyncio
import aiohttp
from typing import Optional, Dict, Any
from .config import settings


class LLMHandler:
    """Handle communication with OpenWebUI local LLM"""

    def __init__(self):
        """Initialize LLM handler"""
        self.base_url = settings.openweb_ui_url
        self.model = settings.openweb_ui_model

    async def query_llm(self, prompt: str) -> str:
        """
        Send a prompt to the local LLM and get response using OpenWebUI API

        Args:
            prompt: User query

        Returns:
            LLM response text
        """
        try:
            async with aiohttp.ClientSession() as session:
                # OpenWebUI chat/completions endpoint (standard OpenAI-compatible)
                url = f"{self.base_url}/api/chat/completions"

                headers = {
                    "Authorization": f"Bearer {settings.openweb_ui_api_key}"
                }

                payload = {
                    "model": self.model,
                    "messages": [
                        {"role": "system", "content": "You are a place search helper. Your ONLY job is to:\n1. Take the user's search term\n2. Keep it EXACTLY as is\n3. Add 'restaurant' if it's a food/dish name\n4. Return ONLY the search query, nothing else\n\nExamples:\n- Input: 'Nasi Goreng' → Output: 'Nasi Goreng restaurant'\n- Input: 'coffee' → Output: 'coffee shop'\n- Input: 'park' → Output: 'park'\n- Input: 'I want pizza' → Output: 'pizza restaurant'\n\nDO NOT change or interpret the user's words. Keep the exact food/place name they mentioned."},
                        {"role": "user", "content": prompt}
                    ],
                    "max_tokens": 50,
                    "temperature": 0.1,
                    "stream": False
                }

                async with session.post(url, json=payload, headers=headers, timeout=30) as response:
                    if response.status == 200:
                        data = await response.json()
                        # Extract text from OpenWebUI response
                        message = data.get("choices", [{}])[0].get("message", {})
                        return message.get("content", "").strip()
                    else:
                        error_text = await response.text()
                        return f"Error: LLM returned status {response.status}: {error_text}"

        except asyncio.TimeoutError:
            return "Error: LLM request timed out. Make sure OpenWebUI is running at " + settings.openweb_ui_url
        except Exception as e:
            return f"Error communicating with LLM: {str(e)}"

    @staticmethod
    def extract_place_query(llm_response: str) -> str:
        """
        Extract/clean place query from LLM response
        LLM should respond with a place name or category directly

        Args:
            llm_response: Response from LLM

        Returns:
            Clean place query for Google Maps API
        """
        # Remove common error messages and suffixes
        response = llm_response.strip()

        # If LLM says it can't help, return empty
        if any(phrase in response.lower() for phrase in
               ["i can't", "unable to", "don't know", "not sure"]):
            return ""

        # Remove "searching for:" or similar prefixes
        if ":" in response:
            response = response.split(":", 1)[1].strip()

        # Take first line if multiple lines
        response = response.split("\n")[0].strip()

        # Remove quotes if present
        response = response.strip('"\'')

        return response


# Global instance
llm_handler = LLMHandler()
