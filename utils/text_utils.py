import re


def normalize_text(text):
    """
    텍스트 정규화 함수
    """

    if text is None:
        return None

    if not isinstance(text, str):
        return None

    # null 문자 제거
    text = text.replace("\x00", " ")

    # 줄바꿈 정리
    text = text.replace("\r\n", "\n")
    text = text.replace("\r", "\n")

    # 여러 줄 → 한 줄
    text = " ".join(text.splitlines())

    # 여러 공백 제거
    text = re.sub(r"\s+", " ", text)

    # 앞뒤 공백 제거
    text = text.strip()

    if len(text) == 0:
        return None

    return text