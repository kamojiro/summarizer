from typing import Literal


def which_url(text: str) -> Literal["html"] | None:
    if not text:
        raise ValueError("テキストが指定されていません")
    if text.startswith("https://"):
        # TODO pdf or html or ...
        return "html"
    else:
        return None
