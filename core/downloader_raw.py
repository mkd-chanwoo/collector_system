import os
import json
from datetime import datetime, timezone, timedelta


class DownloadCheckpoint:
    """
    Download checkpoint manager
    - dataset별 다운로드 진행 상태 관리
    """

    def __init__(self, path="download_checkpoint/download_checkpoint.json"):
        self.path = path
        os.makedirs(os.path.dirname(self.path), exist_ok=True)

    def load(self):
        """
        checkpoint 불러오기
        """
        if not os.path.exists(self.path):
            return None

        with open(self.path, "r", encoding="utf-8") as f:
            return json.load(f)

    def save(self, dataset_name, index, status="running"):
        """
        checkpoint 저장
        """
        KST = timezone(timedelta(hours=9))
        updated_at = datetime.now(KST).isoformat()
        state = {
            "dataset": dataset_name,
            "last_index": index,
            "status": status,
            "updated_at": updated_at
        }

        with open(self.path, "w", encoding="utf-8") as f:
            json.dump(state, f, indent=2, ensure_ascii=False)

    def clear(self):
        """
        완료 시 checkpoint 제거
        """
        if os.path.exists(self.path):
            os.remove(self.path)

    def is_resume(self, dataset_name):
        """
        resume 여부 확인
        """
        state = self.load()

        if not state:
            return False

        return state.get("dataset") == dataset_name

    def get_index(self):
        """
        resume 시작 index 반환
        """
        state = self.load()

        if not state:
            return 0

        return state.get("last_index", 0)


class IntegrityValidator:
    """
    Raw data integrity validator

    Checks:
    - JSONL parsing
    - corrupted line detection
    - total line count
    """

    def __init__(self, log_dir="logs/downloader_log"):
        self.log_dir = log_dir
        os.makedirs(self.log_dir, exist_ok=True)

    def validate(self, file_path, dataset_name):
        total_lines = 0
        corrupted_lines = 0
        encoding_errors = 0

        if not os.path.exists(file_path):
            print(f"[ERROR] File not found: {file_path}")
            return False

        # 🔥 핵심: binary로 읽고 직접 decode
        with open(file_path, "rb") as f:
            for i, raw_line in enumerate(f):

                try:
                    line = raw_line.decode("utf-8")
                except UnicodeDecodeError:
                    encoding_errors += 1
                    print(f"[ENCODING ERROR] line {i}")
                    continue

                # replacement char 체크
                if "�" in line:
                    encoding_errors += 1

                try:
                    json.loads(line)
                    total_lines += 1
                except Exception:
                    corrupted_lines += 1
                    print(f"[CORRUPTED] line {i}")

        valid = (corrupted_lines == 0) and (encoding_errors == 0)

        result = {
            "dataset": dataset_name,
            "file_path": file_path,
            "total_lines": total_lines,
            "corrupted_lines": corrupted_lines,
            "encoding_errors": encoding_errors,
            "valid": valid,
            "timestamp": datetime.now().isoformat()
        }

        self._save_log(dataset_name, result)

        print(
            f"[VALIDATION] {dataset_name} | lines={total_lines} "
            f"| corrupted={corrupted_lines} | encoding_errors={encoding_errors}"
        )
        
        if encoding_errors / total_lines > 0.05:
            valid = False

        return valid

    def _save_log(self, dataset_name, result):
        safe_name = dataset_name.replace("/", "_")

        log_path = os.path.join(self.log_dir, f"{safe_name}.json")

        with open(log_path, "w", encoding="utf-8") as f:
            json.dump(result, f, indent=2, ensure_ascii=False)