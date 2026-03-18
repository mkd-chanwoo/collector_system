import sentencepiece as spm


class TokenCounter:
    """
    SentencePiece tokenizer 기반 token counting 모듈 ----- mkd tokenizer로 변환 해야됨.
    """

    def __init__(self, tokenizer_path):

        try:

            self.sp = spm.SentencePieceProcessor()
            self.sp.load(tokenizer_path)

        except Exception as e:

            raise RuntimeError(
                f"Failed to load tokenizer: {e}"
            )

    def count(self, text):
        """
        텍스트 → token 개수 계산
        """

        if text is None:
            return 0

        try:

            tokens = self.sp.encode(text)

            return len(tokens)

        except Exception:

            return 0