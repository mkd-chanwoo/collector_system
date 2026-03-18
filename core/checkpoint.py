import json
from pathlib import Path
from datetime import datetime, timezone, timedelta, UTC

class Savepoint:

    def __init__(self, path="checkpoints/pipeline_checkpoint.json",
                history_path="state/history.jsonl"):

        self.path = Path(path)
        self.history_path = Path(history_path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.history_path.parent.mkdir(parents=True, exist_ok=True)

    # =========================
    # snapshot
    # =========================
    def load(self):

        if not self.path.exists():
            return None

        try:
            with open(self.path, "r") as f:
                content = f.read().strip()
                if not content:
                    return None
                return json.loads(content)
        except:
            return None

    def save(self, state):

        # snapshot 저장 (atomic)
        temp_path = self.path.with_suffix(".tmp")

        with open(temp_path, "w") as f:
            json.dump(state, f, indent=2)

        temp_path.replace(self.path)

        # history 저장 (append)
        self._append_history(state)

    # =========================
    # history
    # =========================
    def _append_history(self, state):
        KST = timezone(timedelta(hours=9))
        updated_at = datetime.now(KST).isoformat()
        log = {
            "timestamp": updated_at,
            "dataset": state.get("dataset"),
            "total_docs": state.get("total_docs"),
            "total_tokens": state.get("total_tokens"),
            "stats_tmp": state.get("stats_tmp"),
            "quota_state": state.get("quota_state")
        }

        with open(self.history_path, "a") as f:
            f.write(json.dumps(log) + "\n")

    def clear(self):

        if self.path.exists():
            self.path.unlink()