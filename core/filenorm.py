import os
from datetime import datetime, UTC
import json

class NormalizeCheckpoint:

    def __init__(self, path="/home/work/trainee/collector_system/collector_system/normailizer_checkpoint/normalize_checkpoint.json"):
        self.path = path
        os.makedirs(os.path.dirname(path), exist_ok=True)

    def load(self):
        if not os.path.exists(self.path):
            return None
        with open(self.path) as f:
            return json.load(f)

    def save(self, dataset, line_idx, doc_id):
        state = {
            "dataset": dataset,
            "line_index": line_idx,
            "doc_id": doc_id,
            "updated_at": datetime.now(UTC).isoformat()
        }
        with open(self.path, "w") as f:
            json.dump(state, f, indent=2)

    def is_resume(self, dataset):
        state = self.load()
        return state and state["dataset"] == dataset

    def get(self):
        state = self.load()
        if not state:
            return 0, 0
        return state["line_index"], state["doc_id"]