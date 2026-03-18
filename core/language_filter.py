import fasttext
from langdetect import detect


class LanguageFilter:
    """
    언어 필터링 모듈
    """

    def __init__(self, model_path):
        """
        FastText language detection 모델 로드
        """

        try:
            self.model = fasttext.load_model(model_path)

        except Exception as e:
            raise RuntimeError(
                f"Failed to load FastText language model: {e}"
            )

    def detect_language(self, text):
        """
        FastText 기반 언어 감지
        """

        try:

            clean_text = "".join(c for c in text if c.isprintable())
            clean_text = clean_text.replace("\n", " ").replace("\t", " ").strip()

            prediction = self.model.predict(clean_text[:1000])

            lang = prediction[0][0].replace("__label__", "")
            confidence = float(prediction[1][0])

        except Exception as e:

            print("FASTTEXT ERROR:", e)

            lang = self.fallback(text)
            confidence = 0.5

        return lang, confidence

    def fallback(self, text):
        """
        FastText 실패 시 langdetect fallback
        """

        try:
            return detect(text)

        except Exception:
            return "unknown"