import os
import json
from datetime import datetime, UTC
from tqdm import tqdm
import logging

from core.source_manager import SourceManager
from core.downloader_raw import DownloadCheckpoint, IntegrityValidator
from core.monitoring import enable_file_logging
from core.downloader_nonstreaming import Downloader

# from core.downloader_raw import DownloaderRaw


# =========================
# JSONL writer
# =========================
def append_jsonl(path, data):
    with open(path, "a", encoding="utf-8") as f:
        f.write(json.dumps(data, ensure_ascii=False, default=str) + "\n")


# =========================
# HF streaming → raw dump
# =========================
def dump_streaming_dataset(dataset, save_path, limit=None):
    """
    dataset: huggingface streaming dataset
    save_path: data.jsonl 경로
    limit: 테스트용 제한
    """
    count = 0

    for sample in tqdm(dataset, desc="Dumping raw dataset"):
        append_jsonl(save_path, sample)

        count += 1
        if limit and count >= limit:
            break

    return count


# =========================
# metadata 저장
# =========================
def save_metadata(meta_path, source_config, total_count):
    metadata = {
        "source": source_config.get("hf_name"),
        "config": source_config.get("config"),
        "split": source_config.get("split"),
        "domain": source_config.get("domain"),
        "url": source_config.get("url"),
        "method": "hf_nonstreaming_dump",
        "download_time": datetime.now(UTC).isoformat(),
        "total_samples": total_count,
    }

    with open(meta_path, "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2, ensure_ascii=False, default=str)

def get_line_count(path):
    if not os.path.exists(path):
        return 0
    with open(path, "r", encoding="utf-8") as f:
        return sum(1 for _ in f)

# =========================
# main downloader
# =========================
def run_downloader():
    os.makedirs("logs/downloader_log", exist_ok=True)
    enable_file_logging("logs/downloader_log/downloader.log")
    logger = logging.getLogger(__name__)
    
    logger.info("\n===== RAW DATA DOWNLOADER START =====\n")
    checkpoint = DownloadCheckpoint()
    integrity = IntegrityValidator()

    source_manager = SourceManager("config/datasets.yaml")
    sources = source_manager.list_sources()

    # HF loader (기존 downloader 재사용)
    hf_loader = Downloader() # ------------------ 고치는 부분 

    total_datasets = sum(
        1 for s in sources.values() if s.get("approved") is not False
    )
    dataset_idx = 0

    global_bar = tqdm(
        total=total_datasets,
        desc="GLOBAL",
        position=0,
        dynamic_ncols=True
    )

    for name, source in sources.items():
        # -------------------------
        # 경로 설정
        # -------------------------
        raw_dir = os.path.join("data/raw", name)
        os.makedirs(raw_dir, exist_ok=True)

        safe_name = name.replace("/", "_")

        data_path = os.path.join(raw_dir, f"{safe_name}.jsonl")
        meta_path = os.path.join(raw_dir, f"{safe_name}_metadata.json")

        if checkpoint.is_resume(name):
            file_lines = get_line_count(data_path)
            start_idx = max(checkpoint.get_index(), file_lines)
            logger.info(f"[RESUME] from index {start_idx}")
        else:
            start_idx = get_line_count(data_path)

        # 승인 안된건 스킵 (있으면)
        if source.get("approved") is False:
            logger.info(f"[SKIP] {name} not approved")
            continue

        dataset_idx += 1
        logger.info(f"\n[INFO] Processing dataset: {name}")

        

        # 이미 존재하면 스킵 (재다운로드 방지)
        if os.path.exists(data_path) and not checkpoint.is_resume(name):
            logger.info(f"[SKIP] Raw already exists: {data_path}")
            continue

        # -------------------------
        # HF Downloading
        # -------------------------
        try:
            dataset = hf_loader.load_dataset(source)
            # 다운로드 강제 실행
            logger.info(f"[DOWNLOAD START] {name}")
            total_len = len(dataset)
            logger.info(f"[DOWNLOAD DONE] {name} | total={total_len}")
        except Exception as e:
            logger.info(f"[ERROR] Failed to load dataset {name}: {e}")
            continue

        # -------------------------
        # dump raw
        # -------------------------
        total = file_lines = get_line_count(data_path)

        if start_idx > 0:
                dataset = dataset.select(range(start_idx, total_len))

        start_time = datetime.now(UTC)
        pbar = tqdm(
            dataset,
            total=(total_len - start_idx),
            desc=f"[{dataset_idx}/{total_datasets}] {name} ({source.get('domain')})",
            position=1,
            dynamic_ncols=True,
            leave=False
        )

        for sample in pbar:
            

            append_jsonl(data_path, sample)
            total += 1

            if total % 100 == 0:
                elapsed = (datetime.now(UTC) - start_time).total_seconds()
                processed = total - start_idx
                speed = processed / elapsed if elapsed > 0 else 0
                eta = (total_len - total) / speed if speed > 0 else 0
                progress = (total / total_len) * 100

                pbar.set_postfix({
                    "%": f"{progress:.2f}",
                    "done": total,
                    "spd": f"{speed:.0f}/s",
                    "eta(s)": f"{eta:.0f}"
                })

            # checkpoint 저장
            if total % 10000 == 0:
                checkpoint.save(name, total)
                logger.info(f"[SAVEPOINT] {name} | total={total}")
                print(f"[SAVEPOINT] {name} | total={total}")
            # integrity.validate(data_path, name)

            # # 테스트 제한
            # if total >= 8000:
            #     break
        global_bar.update(1)

        global_progress = (dataset_idx / total_datasets) * 100

        global_bar.set_postfix({
            "%": f"{global_progress:.1f}",
            "last": name,
            "domain": source.get("domain")
        })

        checkpoint.save(name, total if total > 0 else 0, status="completed")

        # -------------------------
        # metadata 저장
        # -------------------------
        try:
            integrity.validate(data_path, name)
        except Exception as e:
            logger.info(f"[ERROR] Integrity validation failed: {e}")

        try:
            save_metadata(meta_path, source, total)
        except Exception as e:
            logger.info(f"[ERROR] Metadata save failed: {e}")
        
        
        

        logger.info(f"[DONE] {name} → {total} samples saved")
        checkpoint.clear() # 나중에 주석 제거
        pbar.close()
    global_bar.close()
    logger.info("\n===== RAW DATA DOWNLOADER COMPLETE =====\n")


# =========================
# entry
# =========================
if __name__ == "__main__":
    run_downloader()