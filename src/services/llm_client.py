from openai import OpenAI
import os
from loguru import logger
import time

class OpenRouterClient:
    def __init__(self, api_key):
        self.client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=api_key,
        )
        # Robust pool of free models
        self.model_pool = [
            "meta-llama/llama-3.3-70b-instruct",
            "tngtech/deepseek-r1t2-chimera",
            "openai/gpt-oss-120b",
            "google/gemma-3-27b",
            "qwen/qwen3-coder-480b-a35b"
        ]

    def chat(self, messages):
        last_error = ""
        for model in self.model_pool:
            try:
                logger.info(f"Attempting request with model: {model}")
                completion = self.client.chat.completions.create(
                    model=model,
                    messages=messages,
                    # FIX: Use extra_headers instead of headers
                    extra_headers={
                        "HTTP-Referer": "https://github.com/timesheets-companion-assistant",
                        "X-Title": "timesheets-companion Assistant"
                    },
                    timeout=45
                )
                
                if completion and completion.choices and completion.choices[0].message.content:
                    logger.success(f"Success with model: {model}")
                    return completion.choices[0].message.content
                
                logger.warning(f"Model {model} returned an empty response.")
                
            except Exception as e:
                last_error = str(e)
                logger.error(f"Failure with model {model}: {last_error}")
                continue
        
        return f"Error: All available free models failed. Last error: {last_error}. Please try again in a few moments."
