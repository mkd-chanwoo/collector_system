import os
import json

class Sharder:
    """
    JSONL shard 생성 모듈
    """

    def __init__(self, output_dir, shard_size=10000):

        self.output_dir = output_dir
        self.shard_size = shard_size

        os.makedirs(self.output_dir, exist_ok=True)

        self.current_docs = []
        self.shard_index = self._recover_shard_index()
        self.current_tokens = 0

        self.meta_dir = os.path.join(self.output_dir, "meta")
        os.makedirs(self.meta_dir, exist_ok=True)

    def _recover_shard_index(self):

        files = os.listdir(self.output_dir)

        shard_files = [
            f for f in files
            if f.startswith("shard_") and f.endswith(".jsonl") and f != "shard_meta.jsonl"
        ]

        if not shard_files:
            return 0

        indices = []

        for f in shard_files:

            try:
                idx = int(f.replace("shard_", "").replace(".jsonl", ""))
                indices.append(idx)
            except:
                continue

        if not indices:
            return 0

        return max(indices) + 1

    def add_document(self, doc, tokens):
        """
        문서를 shard buffer에 추가
        """

        self.current_docs.append(doc)
        self.current_tokens += tokens

        if len(self.current_docs) >= self.shard_size:
            self.flush()

    def flush(self):
        """
        shard 파일 생성
        """
        if not self.current_docs:
            return

        doc_count = len(self.current_docs)
        token_count = self.current_tokens

        shard_name = f"shard_{self.shard_index:06d}.jsonl"

        path = os.path.join(self.output_dir, shard_name)
        path_meta = os.path.join(self.meta_dir, "shard_meta.jsonl")

        with open(path, "w", encoding="utf-8") as f:

            for doc in self.current_docs:

                f.write(json.dumps(doc, ensure_ascii=False) + "\n")

        with open(path_meta, "a", encoding="utf-8") as m:
            metadata = {"shard_id":shard_name,
                        "doc_count":doc_count,
                        "token_count":token_count}
            m.write(json.dumps(metadata, ensure_ascii=False) + "\n")

        print(f"Shard saved: {path}")

        self.current_docs = []
        self.shard_index += 1
        self.current_tokens = 0