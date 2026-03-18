import string


class Auditor:

    def __init__(self):

        self.required_fields = [
            "doc_id",
            "source",
            "domain",
            "text",
            "char_count",
            "tokens_count"
        ]

    def validate_document(self, doc):

        if not isinstance(doc, dict):
            return False

        # 필드 존재 확인
        for field in self.required_fields:
            if field not in doc:
                return False

        text = doc["text"]

        # text type
        if not isinstance(text, str):
            return False

        if not text.strip():
            return False

        # encoding check
        try:
            text.encode("utf-8")
        except UnicodeError:
            return False

        # char count verification
        if doc["char_count"] != len(text):
            return False

        # token count verification
        if doc["tokens_count"] <= 0:
            return False

        # broken text detection
        printable_ratio = sum(c in string.printable for c in text) / len(text)

        if printable_ratio < 0.7:
            return False

        return True