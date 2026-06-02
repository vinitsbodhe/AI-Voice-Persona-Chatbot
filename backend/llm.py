from google import genai
from backend import config

class LLMManager:
    def __init__(self):
        if not config.GEMINI_API_KEY:
            raise ValueError("GEMINI_API_KEY is not set.")

        self.client = genai.Client(
            api_key=config.GEMINI_API_KEY
        )

    def generate_response(self, system_prompt: str, history: list, user_message: str) -> str:

        history_text = "\n".join(
            [f"{msg['role']}: {msg['content']}" for msg in history]
        )

        prompt = f"""
{system_prompt}

Conversation History:
{history_text}

User Question:
{user_message}
"""

        response = self.client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt
        )

        return response.text