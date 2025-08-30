import os
from http import HTTPStatus

import requests
from dotenv import load_dotenv
from fastapi import HTTPException
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
            print("message:", message.content.strip())
            await self.message_summary(message.content.strip())
        return messages

    async def _post_to_misskey(self, body: dict[str, str]):
        headers = {"Content-Type": "application/json"}
        kamomai_url = f"https://{self.missky_host}/api"
        response = requests.post(
            f"{kamomai_url}/notes/create", headers=headers, json=body, timeout=5
        )
        if response.status_code != HTTPStatus.OK:
            raise ValueError(
                "Error posting to Misskey:", response.status_code, response.text
            )
        return response.json()["createdNote"]["id"]

    async def message_summary(self, message):
        texts: list[str] = self.ai_searvice.generate_content_if(message)
        body = {
            "i": self.missky_token,
            "visibility": "home",
        }
        message_id: str | None = None
        for text in texts:
            body["text"] = text
            if message_id:
                body["replyId"] = message_id
            try:
                message_id = await self._post_to_misskey(body)
            except Exception as e:
                print("Error posting to Misskey:", text)
                raise e
