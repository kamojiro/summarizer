import os

import requests
from dotenv import load_dotenv

load_dotenv()


class MisskyService:
    def __init__(self):
        self.missky_host = os.getenv("MISSKY_HOST")
        self.missky_token = os.getenv("MISSKY_TOKEN")

    async def message_sumamry(self):
        headers = {"Content-Type": "application/json"}
        url = f"https://{self.missky_host}/api"

        text = "Hello, World!"
        body = {
            "i": self.missky_host,
            "visibility": "home",
            "text": text,
        }
        requests.post(f"{url}/notes/create", headers=headers, json=body, timeout=5)
        return text
