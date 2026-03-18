from datasketch import MinHash, MinHashLSH
import hashlib


class Deduplicator:
    """
    데이터 중복 제거 모듈
    """

    def __init__(self, threshold=0.85, num_perm=128):

        self.threshold = threshold
        self.num_perm = num_perm

        # Exact duplicate 추적
        self.seen_hashes = set()

        # Near duplicate 탐지
        self.lsh = MinHashLSH(
            threshold=self.threshold,
            num_perm=self.num_perm
        )
        
        self.total_docs = 0
        self.exact_removed = 0
        self.near_removed = 0

    def _hash_text(self, text):
        """
        SHA256 해시 생성
        """

        return hashlib.sha256(
            text.encode("utf-8")
        ).hexdigest()

    def is_exact_duplicate(self, text):
        """
        Exact duplicate 검사
        """

        h = self._hash_text(text)

        if h in self.seen_hashes:
            return True

        self.seen_hashes.add(h)

        return False

    def _create_minhash(self, text):
        """
        MinHash 생성
        """

        m = MinHash(num_perm=self.num_perm)

        words = text.split()

        if len(words) < 3:
            return None

        shingles = zip(*(words[i:] for i in range(3)))

        for shingle in shingles:
            m.update(" ".join(shingle).encode("utf8"))

        return m

    def is_near_duplicate(self, text, doc_id):
        """
        Near duplicate 검사
        """

        m = self._create_minhash(text)

        if m is None:
            return False

        result = self.lsh.query(m)

        if result:
            return True

        self.lsh.insert(str(doc_id), m)

        return False