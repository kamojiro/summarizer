import os

import requests
from dotenv import load_dotenv
from langchain_community.document_loaders import WebBaseLoader
from vertexai.generative_models import GenerationConfig, GenerativeModel, Tool

from services.ai_service import AIService
from utils.url_validator import which_url

load_dotenv()

PROJECT_ID = os.getenv("PROJECT_ID")
REGION = os.getenv("REGION")

if not PROJECT_ID or not REGION:
    raise ValueError(
        "Environment variables PROJECT_ID and REGION must be set for Vertex AI."
    )

load_dotenv()


class MisskeyService:
    def __init__(self):
        self.missky_host = os.getenv("MISSKY_HOST")
        self.missky_token = os.getenv("MISSKY_TOKEN")
        self.ai_searvice = AIService()
    async def message_summaries(self, messages):
        for message in messages:
            await self.message_summary(message.content.strip())
        return messages

    async def message_summary(self, message):
        text = self.ai_searvice.generate_content_if(message)

        headers = {"Content-Type": "application/json"}
        kamomai_url = f"https://{self.missky_host}/api"
        body = {
            "i": self.missky_token,
            "visibility": "followers",
            "text": text,
        }
        requests.post(
            f"{kamomai_url}/notes/create", headers=headers, json=body, timeout=5
        )
