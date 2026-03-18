import os
from tqdm import tqdm
from datetime import datetime, timezone, timedelta, UTC
import json

from core.source_manager import SourceManager
from pipeline.run_pipeline import load_jsonl_stream 
from core.filenorm import NormalizeCheckpoint

def get_line_count(path):
    if not os.path.exists(path):
        return 0
    with open(path, "r", encoding="utf-8") as f:
        return sum(1 for _ in f)

def run_normalizer():

    print("\n===== NORMALIZATION START =====\n")

    source_manager = SourceManager("config/datasets.yaml")
    sources = source_manager.list_sources()
    checkpoint = NormalizeCheckpoint()

    for name, source in sources.items():

        safe_name = name.replace("/", "_")

        raw_path = f"data/raw/{name}/{safe_name}.jsonl"
        output_dir = "data/normalized"
        os.makedirs(output_dir, exist_ok=True)

        output_path = f"{output_dir}/{safe_name}.jsonl"

        dataset = load_jsonl_stream(raw_path)

        if not os.path.exists(raw_path):
            print(f"[SKIP] No raw data: {name}")
            continue

        if os.path.exists(output_path) and not checkpoint.is_resume(name):
            print(f"[SKIP] Already normalized: {name}")
            continue

        file_lines = get_line_count(output_path)

        if checkpoint.is_resume(name):
            start_idx_ckpt, doc_id_ckpt = checkpoint.get()
            start_idx = max(start_idx_ckpt, file_lines)
            doc_id = max(doc_id_ckpt, file_lines)
        else:
            start_idx = file_lines
            doc_id = file_lines
   
        mode = "a" if os.path.exists(output_path) else "w"
        with open(output_path, mode, encoding="utf-8") as f_out:

            for i, sample in enumerate(tqdm(dataset, desc=f"Normalizing {name}")):
                if i < start_idx:
                    continue
                text = sample.get(source["field"], None)

                if text is None:
                        continue
                KST = timezone(timedelta(hours=9))
                updated_at = datetime.now(KST).isoformat()
                doc = {
                    "doc_id": f"{safe_name}_{doc_id}",
                    "source_name": name,
                    "domain": source.get("domain"),
                    "language": source.get("language"),
                    "title": sample.get("title"),
                    "text": text,
                    "url": sample.get("url"),
                    "license": source.get("license"),
                    "timestamp": updated_at,
                    "raw_path": raw_path,
                    "processing_version": "v1"
                }

                f_out.write(json.dumps(doc, ensure_ascii=False) + "\n")

                doc_id += 1

                if i % 1000 == 0:
                    checkpoint.save(name, i, doc_id)

        checkpoint.save(name, i, doc_id)
        print(f"[NORMALIZED] {name} → {doc_id} docs")

    print("\n===== NORMALIZATION COMPLETE =====\n")


if __name__ == "__main__":
    run_normalizer()