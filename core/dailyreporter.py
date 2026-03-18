import os
import json
import csv
from datetime import datetime, timezone, timedelta



class DailyReporter:
    """
    Daily Summary Export (5.7)
    Pipeline 진행 상황 리포트 생성 모듈
    """

    def __init__(self, output_dir):

        self.output_dir = output_dir

        os.makedirs(self.output_dir, exist_ok=True)

        self.live_budget_path = os.path.join(output_dir, "token_budget_live.json")
        self.domain_progress_path = os.path.join(output_dir, "domain_progress.json")
        self.source_contribution_path = os.path.join(output_dir, "source_contribution.csv")
        self.daily_csv_path = os.path.join(output_dir, "token_budget_daily.csv")


    def export(self, quota_controller, shard_index):
        """
        shard 생성 시 호출되는 메인 export 함수
        """

        total_tokens = quota_controller.get_total_tokens()
        domain_tokens = quota_controller.domain_tokens
        source_tokens = quota_controller.source_tokens
        targets = quota_controller.target

        self._export_live_budget(total_tokens, domain_tokens, shard_index)
        self._export_domain_progress(domain_tokens, targets)
        self._export_source_contribution(source_tokens)
        self._export_daily_snapshot(total_tokens)


    def _export_live_budget(self, total_tokens, domain_tokens, shard_index):
        KST = timezone(timedelta(hours=9))
        updated_at = datetime.now(KST).isoformat()
        data = {
            "timestamp": updated_at,
            "total_tokens": total_tokens,
            "shards_written": shard_index,
            "domains": domain_tokens
        }

        with open(self.live_budget_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)


    def _export_domain_progress(self, domain_tokens, targets):

        progress = {}

        for domain, tokens in domain_tokens.items():

            target = targets.get(domain, 0)

            if target > 0:
                ratio = tokens / target
            else:
                ratio = 0

            progress[domain] = {
                "tokens": tokens,
                "target": target,
                "progress": ratio
            }

        with open(self.domain_progress_path, "w", encoding="utf-8") as f:
            json.dump(progress, f, ensure_ascii=False, indent=2)


    def _export_source_contribution(self, source_tokens):

        with open(self.source_contribution_path, "w", newline="", encoding="utf-8") as f:

            writer = csv.writer(f)

            writer.writerow(["domain", "source", "tokens"])

            for domain, sources in source_tokens.items():

                for source, tokens in sources.items():

                    writer.writerow([domain, source, tokens])


    def _export_daily_snapshot(self, total_tokens):

        today = datetime.utcnow().date().isoformat()

        file_exists = os.path.exists(self.daily_csv_path)

        with open(self.daily_csv_path, "a", newline="", encoding="utf-8") as f:

            writer = csv.writer(f)

            if not file_exists:
                writer.writerow(["date", "total_tokens"])

            writer.writerow([today, total_tokens])