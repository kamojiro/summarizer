from json import load

import pytest

from src.services.ai_service import AIService


def test_ai_service_initialization():
    ai_service = AIService()
    assert ai_service.client is not None
    assert ai_service.model == "gemini-2.5-pro"


def test_ai_service_generate_content():
    ai_service = AIService()
    prompt = "こんにちは、元気ですか？"
    answer = ai_service.generate_content_if(prompt)

    print("Generated content:", answer)


def test_ai_searvice_generate_content_with_url():
    ai_service = AIService()
    prompt = "必要ならURLを検索して回答してください。https://blog.g-gen.co.jp/entry/migrate-from-vertex-ai-sdk-to-google-gen-ai-sdk"
    answer = ai_service.generate_content_if(prompt)
    print("Generated content with URL:", answer)


def test_ai_searvice_generate_content_with_search():
    ai_service = AIService()
    prompt = "2025年の甲子園の優勝校が決まったので検索して教えてください。検索ツールを利用してください"
    answer = ai_service.generate_content_if(prompt)
    print("Generated content with search:", answer)


def test_ai_searvice_generate_content_with_url2():
    ai_service = AIService()
    prompt = "https://www.kanaloco.jp/news/culture/bunka/article-1201513.html"
    answer = ai_service.generate_content_if(prompt)
    print("Generated content with search:", answer)
