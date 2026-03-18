import re
import trafilatura
from simhash import Simhash, SimhashIndex
from collections import Counter
import math

BOILERPLATE_PHRASES = [
            "accept cookies",
            "cookie policy",
            "privacy policy",
            "terms of service",
            "all rights reserved"
        ]


class QualityFilter:
    """
    텍스트 품질 필터링 모듈
    """

    def __init__(self, min_chars=200, max_chars=200000, simhash_threshold=8):

        self.min_chars = min_chars
        self.max_chars = max_chars
        self.simhash_threshold = simhash_threshold

        # 이전 문서 hash 저장 (template detection)
        self.index = SimhashIndex([], k=simhash_threshold)
        self.doc_id = 0

        # URL 패턴
        self.url_pattern = re.compile(r"http[s]?://")

        # HTML 태그 패턴
        self.html_pattern = re.compile(r"<[^>]+>")

    def keep(self, text):
        """
        heuristic 품질 검사
        """

        if text is None:
            return False

        length = len(text)

        # 길이 검사
        if length < self.min_chars:
            return False

        if length > self.max_chars:
            return False

        # URL spam 검사
        if len(self.url_pattern.findall(text)) > 5:
            return False

        # HTML tag 과다 검사
        if self.markup_ratio(text) > 0.3:
            return False

        # 문자 다양성 검사
        if self._low_character_diversity(text):
            return False

        # template page 검사
        if self._is_template(text):
            return False

        if self.is_repetitive(text):
            return False

        if self.has_boilerplate(text):
            return False

        if self.low_entropy(text):
            return False

        return True

    def _low_character_diversity(self, text):
        """
        동일 문자 반복 여부 검사
        """

        tokens = text.split()

        if not tokens:
            return True

        return len(set(tokens)) / len(tokens) < 0.2

    def remove_boilerplate(self, text):
        """
        HTML boilerplate 제거
        """

        if not text:
            return None

        # HTML이 아닐 경우 extractor 사용하지 않음
        if "<html" not in text and "<body" not in text and "<div" not in text:
            return text

        try:
            extracted = trafilatura.extract(
                text,
                include_comments=False,
                include_tables=False
            )

            if extracted:
                return extracted

            return text

        except Exception:
            return text

    def _is_template(self, text):
        """
        template / duplicate page 검사 (SimHash)
        """

        h = Simhash(text)

        near = self.index.get_near_dups(h)

        if near:
            return True

        self.index.add(str(self.doc_id), h)
        self.doc_id += 1

        return False

    # def filter(self, text):
    #     """
    #     전체 필터링 파이프라인
    #     """

    #     if text is None:
    #         return None

    #     # boilerplate 제거
    #     text = self.remove_boilerplate(text)

    #     # regex cleanup
    #     text = re.sub(r"<[^>]+>", "", text)
    #     text = re.sub(r"http\S+", "", text)
    #     text = re.sub(r"\S+@\S+", "", text)

    #     if not self.keep(text):
    #         return None

    #     return text

    def repetition_ratio(self, text, n=3):
        tokens = text.split()

        if len(tokens) < n:
            return 0
        
        ngrams = zip(*[tokens[i:] for i in range(n)])

        counts = Counter(ngrams)

        total = sum(counts.values())
        repeated = sum(c for c in counts.values() if c > 1)

        return repeated / total if total else 0

    def is_repetitive(self, text):
        return self.repetition_ratio(text) > 0.2

    def has_boilerplate(self, text):
        text = text.lower()
        return any(p in text for p in BOILERPLATE_PHRASES)

    def low_entropy(self, text):
        """
        Shannon entropy 계산 및 threshold
        """

        if not text:
            return True

        counts = Counter(text)
        total = len(text)

        ent = 0

        for c in counts.values():
            p = c / total
            ent -= p * math.log2(p)

        return ent < 3.5

    def markup_ratio(self, text):

        tags = self.html_pattern.findall(text)

        if not text:
            return 0

        tag_chars = sum(len(t) for t in tags)

        return tag_chars / len(text)