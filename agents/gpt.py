import os
from openai import AzureOpenAI
from dotenv import load_dotenv

load_dotenv()


class GPTClient:

    def __init__(self, model_name: str = None):
        """
        Initializes the Azure OpenAI client.
        Reads credentials from environment variables:
        - AZURE_OPENAI_API_KEY
        - AZURE_OPENAI_ENDPOINT
        - AZURE_OPENAI_API_VERSION (defaults to "2024-02-15-preview")
        - AZURE_OPENAI_DEPLOYMENT / GPT_MODEL (defaults to "gpt-4o")
        """
        self.api_key = os.getenv("AZURE_OPENAI_API_KEY")
        self.endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
        self.api_version = os.getenv("AZURE_OPENAI_API_VERSION", "2024-02-15-preview")
        
        # Determine deployment/model name
        self.model = model_name or os.getenv("AZURE_OPENAI_DEPLOYMENT") or os.getenv("GPT_MODEL", "gpt-4o")

        self.client = AzureOpenAI(
            api_key=self.api_key,
            api_version=self.api_version,
            azure_endpoint=self.endpoint
        )

    def generate(self, prompt: str, mime_type: str = None) -> str:
        """
        Generates content from the model. Matches the GeminiClient interface.
        """
        messages = [
            {"role": "user", "content": prompt}
        ]
        
        # Request JSON format if requested
        response_format = None
        if mime_type == "application/json":
            response_format = {"type": "json_object"}

        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            response_format=response_format
        )
        
        return response.choices[0].message.content
