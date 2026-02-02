from openai import OpenAI
from src.config.settings import settings
from loguru import logger

class OpenRouterService:
    def __init__(self):
        self.client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=settings.OPENROUTER_API_KEY,
        )
        self.model = settings.AI_MODEL

    def chat(self, messages, temperature=0.7):
        try:
            logger.debug(f"Requesting AI completion from {self.model}")
            completion = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                headers={
                    "HTTP-Referer": "https://github.com/timesheets-companion-assistant",
                    "X-Title": "timesheets-companion Assistant"
                },
                temperature=temperature
            )
            return completion.choices[0].message.content
        except Exception as e:
            logger.error(f"AI Service Error: {e}")
            return f"Error: {str(e)}"
