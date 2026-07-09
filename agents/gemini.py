import os

from google import genai
from dotenv import load_dotenv

load_dotenv()  # Load environment variables from .env file

# class GeminiClient:

#     def __init__(self):

#         self.client = genai.Client(
#             api_key=os.getenv("GEMINI_API_KEY")
#         )

#     def generate(
#         self,
#         prompt: str,
#     ) -> str:

#         response = self.client.models.generate_content(
#             model="gemini-3.5-flash",
#             contents=prompt,
#         )

#         return response.text


client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

for model in client.models.list():
    print(model.name)