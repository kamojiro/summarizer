import os
import sys

import pytest

# プロジェクトのルートディレクトリをパスに追加
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from src.utils.url_validator import which_url


class TestWhichUrl:
    def test_empty_text_raises_exception(self):
        """空のテキストが渡された場合、例外が発生することを確認するテスト"""
        with pytest.raises(ValueError) as e:
            which_url("")
        if str(e.value) != "テキストが指定されていません":
            raise AssertionError(
                f"Expected 'テキストが指定されていません', but got {e.value!s}"
            )

    def test_https_url_returns_html(self):
        """https://で始まるURLが渡された場合、'html'が返ることを確認するテスト"""
        result = which_url("https://example.com")
        if result != "html":
            raise AssertionError(f"Expected 'html', but got {result}")

    def test_non_https_url_returns_none(self):
        """https://で始まらないテキストが渡された場合、Noneが返ることを確認するテスト"""
        # http://で始まるURL
        result1 = which_url("http://example.com")
        if result1 is not None:
            raise AssertionError(f"Expected None, but got {result1}")

        # プロトコルなしのURL
        result2 = which_url("example.com")
        if result2 is not None:
            raise AssertionError(f"Expected None, but got {result2}")

        # URLではないテキスト
        result3 = which_url("これはURLではありません")
        if result3 is not None:
            raise AssertionError(f"Expected None, but got {result3}")
