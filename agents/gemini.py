import os
from google import genai
from google.genai import types
from dotenv import load_dotenv

load_dotenv()  # Load environment variables from .env file


class GeminiClient:

    def __init__(self, model_name: str = None):
        if model_name is None:
            model_name = os.getenv("GEMINI_MODEL", "gemini-3.1-flash")
        self.client = genai.Client(
            api_key=os.getenv("GEMINI_API_KEY")
        )
        self.model = model_name

    def generate(self, prompt: str, mime_type: str = None) -> str:
        config = None
        if mime_type:
            config = types.GenerateContentConfig(
                response_mime_type=mime_type
            )
        response = self.client.models.generate_content(
            model=self.model,
            contents=prompt,
            config=config,
        )
        return response.text

