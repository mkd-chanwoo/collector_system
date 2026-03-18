import os
import yaml
from tqdm import tqdm
import json
import time
import logging

from core.source_manager import SourceManager
from core.downloader import Downloader
from core.language_filter import LanguageFilter
from core.quality_filter import QualityFilter
from core.deduplicator import Deduplicator
from core.tokenizer_counter import TokenCounter
from core.quota_controller import QuotaController
from core.sharder import Sharder
from core.auditor import Auditor
from core.reporter import Reporter
from core.MetadataTracker import MetadataTracker
from core.toxicity_filter import ToxicFilter
from core.monitoring import enable_file_logging
from core.checkpoint import Savepoint
from core.dailyreporter import DailyReporter
from core.totalmonitor import Monitoring
from core.resourcemonitor import ResourceMonitor

from utils.text_utils import normalize_text

THISDOMAIN="english"

DOMAIN = {
    "english": 2000000000,
    "korean": 0,
    "code": 0,
    "science": 0} 

MIN_CHAR = 200

def load_jsonl_stream(path):
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            yield json.loads(line)

def load_config():

    with open("config/pipeline_config.yaml") as f:
        pipeline_cfg = yaml.safe_load(f)

    with open("config/datasets.yaml") as f:
        dataset_cfg = yaml.safe_load(f)

    return pipeline_cfg, dataset_cfg

def get_line_count(path):
    if not os.path.exists(path):
        return 0
    with open(path, "r", encoding="utf-8") as f:
        return sum(1 for _ in f)

def initialize_modules(cfg):

    tokenizer = TokenCounter(cfg["tokenizer_path"])

    lang_filter = LanguageFilter("lid.176.bin")

    quality_filter = QualityFilter(
        cfg["quality_filter"]["min_chars"],
        cfg["quality_filter"]["max_chars"]
    )

    deduplicator = Deduplicator(
        threshold=cfg["deduplication"]["similarity_threshold"]
    )

    quota_controller = QuotaController(DOMAIN)

    sharder_path = os.path.join("data", "shards", THISDOMAIN)
    sharder = Sharder(sharder_path)

    auditor = Auditor()

    reporter = Reporter("reports/progress.json")

    downloader = Downloader()

    toxicfilter = ToxicFilter()

    dailyreporter = DailyReporter("reports/Daily")

    monitor = Monitoring("state")

    gpumonitor = ResourceMonitor()

    target_tokens = cfg["global_target_tokens"]

    return {
        "tokenizer": tokenizer,
        "language": lang_filter,
        "quality": quality_filter,
        "dedup": deduplicator,
        "quota": quota_controller,
        "sharder": sharder,
        "auditor": auditor,
        "reporter": reporter,
        "downloader": downloader,
        "toxicfilter": toxicfilter,
        "dailyreporter":dailyreporter,
        "monitor":monitor,
        "resource_monitor":gpumonitor,
        "target_tokens":target_tokens
    }


def run_test_collection():
    enable_file_logging("logs/pipeline_run.log")
    print("\n===== KEURAL DATA PIPELINE RUN =====\n")
    savepoint = Savepoint()
    state = savepoint.load()

    resume_dataset = None
    start_index = 0
    saved_stats = None
    start_time = time.time()

    if state:
        resume_dataset = state.get("dataset")
        saved_stats = state.get("stats_tmp") if state else None

    cfg, datasets_cfg = load_config()

    modules = initialize_modules(cfg)

    if state:
        modules["quota"].load_state(state.get("quota_state"))

    source_manager = SourceManager("config/datasets.yaml")

    sources = source_manager.list_sources()

    source_manager.print_summary()

    stats = {
        "documents": state.get("total_docs", 0) if state else 0,
        "tokens": state.get("total_tokens", 0) if state else 0,
    }

    resume_found = False

    for name, source in sources.items():
        if resume_dataset:

            if not resume_found:

                if name != resume_dataset:
                    continue

                resume_found = True

        print(f"\nLoading dataset: {name}")
        meta_path = "data/meta/"
        safe_name = name.replace("/", "_")
        data_path = f"data/normalized/{safe_name}.jsonl"
        dataset = load_jsonl_stream(data_path)
        modules["downloader"].flush(source, meta_path)
        
        stats_tmp = {
            "documents": 0,
            "tokens": 0,
            "raw_text":0,
            "norm":0,
            "quality":0,
            "lang_confi":0,
            "lang_in":0,
            "dedup_exact":0,
            "dedup_near":0,
            "toxic":0,
            "audit":0

        }
        if saved_stats and name == resume_dataset:
            stats_tmp = saved_stats

        if name == resume_dataset:
            start_index = stats_tmp.get("documents", 0)
        else:
            start_index = 0

        stop_all = False

        for i, sample in enumerate(tqdm(dataset)):
            if i < start_index:
                continue

            if stats["tokens"] >= modules["target_tokens"]:
                stop_all = True
                break
            
            if stats_tmp["documents"] % 500 == 0:
                state = {
                    "dataset": name,
                    "total_docs": stats["documents"],
                    "total_tokens":stats["tokens"],
                    "stats_tmp": stats_tmp.copy(),
                    "quota_state": modules["quota"].to_dict() 
                }
                savepoint.save(state)
                savepoint._append_history(state)
                modules["quota"].summary()
                modules["reporter"].write(stats, stats_tmp)
                modules["sharder"].flush()
                modules["dailyreporter"].export(quota_controller=modules["quota"],
                                                shard_index=modules["sharder"].shard_index)
                modules["monitor"].export(modules["quota"], stats, stats_tmp, modules["sharder"])
                modules["resource_monitor"].log(prefix="PIPELINE")
                stats_resource = modules["resource_monitor"].get_stats()
                elapsed = time.time() - start_time
                tps = stats["tokens"] / elapsed if elapsed > 0 else 0
                print("=======================\n")
                logging.info(
                    f"RESOURCE: {stats_resource} | elapsed={elapsed:.2f}s | tokens/sec={tps:.2f}"
                )
                print("=======================\n")


            t0 = time.time()
            metadatatracker = MetadataTracker(stats_tmp["documents"], meta_path, name)
            raw_text = sample.get("text", None)

            if raw_text is None:
                metadatatracker.record("Non-Text",False,msg="there is no text in this document.")
                metadatatracker.finalize()
                metadatatracker.save()
                stats_tmp["documents"] += 1
                stats_tmp["raw_text"] += 1
                continue
            metadatatracker.record("Non-Text",True,msg="there is text in this document.")
            text = normalize_text(raw_text)

            if text is None:
                metadatatracker.record("Text-Normalization",False,msg="there is no text after normalizing text.")
                metadatatracker.finalize()
                metadatatracker.save()
                stats_tmp["documents"] += 1
                stats_tmp["norm"] += 1
                continue

            bfnormn = len(raw_text)
            afnorm = len(text)
            metadatatracker.record("Text-Normalization",True,before_norm=bfnormn,after_norm=afnorm,difference=bfnormn-afnorm)

            if not modules["quality"].keep(text):
                metadatatracker.record("Quality-Filtering",False,msg="low quality text")
                metadatatracker.finalize()
                metadatatracker.save()
                stats_tmp["documents"] += 1
                stats_tmp["quality"] += 1
                continue
            
            # text = modules["quality"].filter(text)
            metadatatracker.record("Quality-Filtering",True,msg="pass the quality filtering.")

            lang, conf = modules["language"].detect_language(text)

            if conf < 0.7:
                print(conf)
                metadatatracker.record("Language-Filtering",False,lang=lang,confidence=conf,reason="low_confidence")
                metadatatracker.finalize()
                metadatatracker.save()
                stats_tmp["documents"] += 1
                stats_tmp["lang_confi"] += 1
                continue

            if lang != source["language"]: # 바꿔야 되는 부분 - source의 lang과 맞냐 안 맞냐로 하는게 합리적일 수도.....
                metadatatracker.record("Language-Filtering",False,lang=lang,confidence=conf,reason="unsupported_language")
                metadatatracker.finalize()
                metadatatracker.save()
                stats_tmp["documents"] += 1
                stats_tmp["lang_in"] += 1
                continue

            metadatatracker.record("Language-Filtering",True,lang=lang,confidence=conf)

            if modules["dedup"].is_exact_duplicate(text):
                metadatatracker.record("Deduplication",False,reason="duplicate document")
                metadatatracker.finalize()
                metadatatracker.save()
                stats_tmp["documents"] += 1
                stats_tmp["dedup_exact"] += 1
                continue

            doc_name = f"{name}_{stats_tmp['documents']}"

            if modules["dedup"].is_near_duplicate(text, doc_name):
                metadatatracker.record("Deduplication",False,reason="duplicate document")
                metadatatracker.finalize()
                metadatatracker.save()
                stats_tmp["documents"] += 1
                stats_tmp["dedup_near"] += 1
                continue

            metadatatracker.record("Deduplication",True,reason="nonduplicate document")

            if modules["toxicfilter"].badword_filter(text):
                metadatatracker.record("Lexical bad-word filtering",False,reason="there is bad word in this document.")
                metadatatracker.finalize()
                metadatatracker.save()
                stats_tmp["documents"] += 1
                stats_tmp["toxic"] += 1
                continue

            metadatatracker.record("Lexical bad-word filtering",True,reason="there is no bad word in this document.")
            toxicfil, score = modules["toxicfilter"].toxicity_filter(text)

            if toxicfil:
                metadatatracker.record("Toxicity scoring ",False,reason="high toxic", toxic_score=score)
                metadatatracker.finalize()
                metadatatracker.save()
                stats_tmp["documents"] += 1
                stats_tmp["toxic"] += 1
                continue

            metadatatracker.record("Toxicity scoring ",True,reason="low toxic", toxic_score=score)
            tokens = modules["tokenizer"].count(text)

            document = {
                "doc_id": doc_name,
                "source": name,
                "domain": source["domain"],
                "text":text,
                "char_count": len(text),
                "tokens_count": tokens
            }

            if modules["quota"].get_domain_tokens(source["domain"]) > DOMAIN[source["domain"]]:
                print("You have exceeded the allocated token.")
                break

            modules["quota"].update(source["domain"], tokens, name)

            if not modules["auditor"].validate_document(document):
                metadatatracker.record("Auditor",False,reason="rejected")
                metadatatracker.finalize()
                metadatatracker.save()
                stats_tmp["audit"] += 1
                stats_tmp["documents"] += 1
                continue

            metadatatracker.record("Auditor",True,reason="Aceepted")
            metadatatracker.finalize()
            metadatatracker.save()
            modules["sharder"].add_document(document, tokens)

            stats["tokens"] += tokens
            stats_tmp["documents"] += 1
            stats["documents"] += 1

        if name == resume_dataset:
            saved_stats = None
        
        if stop_all:
                break

        modules["reporter"].write(stats, stats_tmp)

    print("\n===== TEST RUN COMPLETE =====")
    print(stats)


if __name__ == "__main__":

    run_test_collection()