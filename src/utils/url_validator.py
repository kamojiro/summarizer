import re
from urllib.parse import urlparse


def is_url(text: str) -> bool:
    """
    与えられたテキストがURLかどうかを判別する関数

    Args:
        text: 判別対象のテキスト

    Returns:
        bool: URLの場合はTrue、そうでない場合はFalse
    """
    if not text:
        return False

    # URLの基本的なパターンをチェック
    pattern = re.compile(
        r"^(?:http|https)://"  # http:// または https:// で始まる
        r"(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|"  # ドメイン
        r"localhost|"  # localhost または
        r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})"  # IPアドレス
        r"(?::\d+)?"  # オプションのポート
        r"(?:/?|[/?]\S+)$",
        re.IGNORECASE,
    )

    if pattern.match(text):
        return True

    # urllib.parseを使用した追加チェック
    try:
        result = urlparse(text)
        return all([result.scheme, result.netloc])
    except ValueError:
        return False
