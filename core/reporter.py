import json
import time
import os


class Reporter:
    """
    파이프라인 진행 상태 기록 모듈
    """

    def __init__(self, output_file):

        self.output_file = output_file

        os.makedirs(os.path.dirname(self.output_file), exist_ok=True)

        self.start_time = time.time()

    def write(self, stats, stats2):
        """
        진행 상태 JSON 파일로 저장
        """

        report = {
            "timestamp": time.time(),
            "elapsed_seconds": time.time() - self.start_time,
            "documents_processed": stats.get("documents", 0),
            "tokens_processed": stats.get("tokens", 0),
            "nontext_document": stats2.get("raw_text", 0),
            "quality_filtering": stats2.get("quality", 0),
            "low_language_confidence": stats2.get("lang_confi", 0),
            "no_eng_kor": stats2.get("lang_in", 0),
            "exactly_duplicate": stats2.get("dedup_exact", 0),
            "near_duplicate": stats2.get("dedup_near", 0),
            "toxic_filtering": stats2.get("toxic", 0),
            "audit": stats2.get("audit", 0),
            "processed_documents_dataset": stats2.get("documents", 0)
        }

        with open(self.output_file, "w", encoding="utf-8") as f:

            json.dump(report, f, indent=2)

        print("\n=== PIPELINE REPORT ===")

        print(f"Documents : {report['documents_processed']:,}")
        print(f"Tokens    : {report['tokens_processed']:,}")
        print(f"Elapsed   : {report['elapsed_seconds']:.2f} sec")
        print(f"processed documents : {report['processed_documents_dataset']:,}")
        print(f"non-text documents    : {report['nontext_document']:,}")
        print(f"quality filtered documents   : {report['quality_filtering']:,} ")
        print(f"low confidence language documents : {report['low_language_confidence']:,}")
        print(f"non English or Korean  : {report['no_eng_kor']:,}")
        print(f"exact deuplicated documents  : {report['exactly_duplicate']:,}")
        print(f"near deuplicated documents : {report['near_duplicate']:,}")
        print(f"toxic_filtered documents  : {report['toxic_filtering']:,}")
        print(f"non-passed documents in audit  : {report['audit']:,} sec")

        print("=======================\n")