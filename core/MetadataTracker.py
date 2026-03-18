from pathlib import Path
import json
import numpy as np

class MetadataTracker:

    def __init__(self, doc_id, path, name):
        self.data = {
            "doc_id": doc_id,
            "filters": {},
            "final_decision": None
        }
        self.path = path
        self.name = name

    def record(self, filter_name, passed, **info):

        self.data["filters"][filter_name] = {
            "passed": passed,
            **info
        }

    def finalize(self):

        passed = all(
            f["passed"] for f in self.data["filters"].values()
        )

        self.data["final_decision"] = "accepted" if passed else "rejected"

        return self.data

    def save(self):
        """
        metadata 파일 저장 (JSONL append)
        """
        path = Path(self.path) / self.name

        path.mkdir(parents=True, exist_ok=True)

        file_path = path / "process.jsonl"

        with open(file_path, "a", encoding="utf-8") as f:
            f.write(
                json.dumps(self.data, default=self._convert, ensure_ascii=False) + "\n"
            )

    def _convert(self, obj):
        if isinstance(obj, (np.float32, np.float64, np.int32, np.int64)):
            return obj.item()   # Python float/int로 변환
        return obj

