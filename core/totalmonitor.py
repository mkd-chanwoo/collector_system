import os
import json
import csv
from datetime import datetime


class Monitoring:
    """
    Monitoring Module (Section 8 대응)

    역할:
    - pipeline 상태를 파일로 export
    - dashboard용 데이터 생성
    """

    def __init__(self, output_dir):

        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)

        self.global_path = os.path.join(output_dir, "global_progress.json")
        self.domain_path = os.path.join(output_dir, "domain_progress.json")
        self.source_path = os.path.join(output_dir, "source_contribution.json")
        self.cleaning_path = os.path.join(output_dir, "cleaning_efficiency.json")
        self.dedup_path = os.path.join(output_dir, "deduplication.json")
        self.error_path = os.path.join(output_dir, "errors.json")
        self.audit_path = os.path.join(output_dir, "audit.json")
        self.throughput_path = os.path.join(output_dir, "throughput.csv")


    def export(self, quota, stats, stats_tmp, sharder):
        """
        메인 함수 (pipeline에서 호출)
        """

        self.global_progress(quota)
        self.domain_progress(quota)
        self.source_contribution(quota)
        self.cleaning_efficiency(stats_tmp)
        self.deduplication(stats_tmp)
        self.error_stats(stats_tmp)
        self.audit_status(stats_tmp)
        self.throughput(stats, sharder)


    # ---------------------------
    # 8.1 Global Progress
    # ---------------------------
    def global_progress(self, quota):

        total = quota.get_total_tokens()
        target = sum(quota.target.values())

        data = {
            "timestamp": datetime.utcnow().isoformat(),
            "total_tokens": total,
            "target_tokens": target,
            "remaining": target - total,
            "progress": total / target if target > 0 else 0
        }

        with open(self.global_path, "w") as f:
            json.dump(data, f, indent=2)


    # ---------------------------
    # 8.2 Domain Progress
    # ---------------------------
    def domain_progress(self, quota):

        result = {}

        for d, tokens in quota.domain_tokens.items():

            target = quota.target.get(d, 0)

            result[d] = {
                "tokens": tokens,
                "target": target,
                "progress": tokens / target if target > 0 else 0
            }

        with open(self.domain_path, "w") as f:
            json.dump(result, f, indent=2)


    # ---------------------------
    # 8.3 Source Contribution
    # ---------------------------
    def source_contribution(self, quota):

        with open(self.source_path, "w") as f:
            json.dump(quota.source_tokens, f, indent=2)


    # ---------------------------
    # 8.4 Cleaning Efficiency
    # ---------------------------
    def cleaning_efficiency(self, stats_tmp):

        raw = stats_tmp["raw_text"]
        cleaned = stats_tmp["documents"]

        data = {
            "raw": raw,
            "cleaned": cleaned,
            "removal_rate": (raw - cleaned) / raw if raw > 0 else 0
        }

        with open(self.cleaning_path, "w") as f:
            json.dump(data, f, indent=2)


    # ---------------------------
    # 8.5 Deduplication
    # ---------------------------
    def deduplication(self, stats_tmp):

        data = {
            "exact": stats_tmp["dedup_exact"],
            "near": stats_tmp["dedup_near"]
        }

        with open(self.dedup_path, "w") as f:
            json.dump(data, f, indent=2)


    # ---------------------------
    # 8.7 Error / Warning
    # ---------------------------
    def error_stats(self, stats_tmp):

        data = {
            "quality_reject": stats_tmp["quality"],
            "lang_low_conf": stats_tmp["lang_confi"],
            "lang_invalid": stats_tmp["lang_in"],
            "toxic": stats_tmp["toxic"]
        }

        with open(self.error_path, "w") as f:
            json.dump(data, f, indent=2)


    # ---------------------------
    # 8.8 Audit Status
    # ---------------------------
    def audit_status(self, stats_tmp):

        data = {
            "audit_reject": stats_tmp["audit"],
            "processed": stats_tmp["documents"]
        }

        with open(self.audit_path, "w") as f:
            json.dump(data, f, indent=2)


    # ---------------------------
    # 8.6 Throughput
    # ---------------------------
    def throughput(self, stats, sharder):

        file_exists = os.path.exists(self.throughput_path)

        with open(self.throughput_path, "a", newline="") as f:

            writer = csv.writer(f)

            if not file_exists:
                writer.writerow(["timestamp", "documents", "tokens", "shards"])

            writer.writerow([
                datetime.utcnow().isoformat(),
                stats["documents"],
                stats["tokens"],
                sharder.shard_index
            ])