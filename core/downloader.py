from datasets import load_dataset
import time
from huggingface_hub import hf_hub_download
import os
import json

class Downloader:
    """
    Dataset downloader module.

    Responsibilities
    ----------------
    - Load datasets from HuggingFace
    - Support streaming and non-streaming datasets
    - Validate dataset configuration
    """

    def __init__(self):
        pass

    def load_dataset(self, source_config):
        """
        Load dataset using configuration
        """

        required_fields = [
            "hf_name",
            "config",
            "split",
            "field",
            "domain",
            "streaming",
            "url"
        ]

        for field in required_fields:
            if field not in source_config:
                raise ValueError(
                    f"Dataset config missing required field: {field}"
                )

        dataset_name = source_config["hf_name"]
        split = source_config["split"]
        streaming = source_config["streaming"]

        print(f"\nLoading dataset: {dataset_name}")
        print(f"Split: {split}")
        print(f"Streaming: {streaming}")

        try:

            config_name = source_config.get("config")

            dataset = load_dataset(
                dataset_name,
                config_name,
                split=split,
                streaming=streaming
            )

        except Exception as e:

            raise RuntimeError(
                f"Failed to load dataset {dataset_name}: {e}"
            )

        return dataset

    def raw_info(self, source_config, save_dir):
        os.makedirs(save_dir, exist_ok=True)
        required_fields = [
                "hf_name",
                "config",
                "split",
                "field",
                "domain",
                "streaming",
                "url"
            ]

        for field in required_fields:
            if field not in source_config:
                raise ValueError(
                    f"Dataset config missing required field: {field}"
                )
            
        filename = source_config["hf_name"]
        url = source_config["url"]
        checksums = None
        download_start = time.time()    
        readme = self.download_dataset_card(source_config, save_dir)
        return {
            "filename":filename,
            "config": source_config.get("config"),
            "split": source_config["split"],
            "url":url,
            "checksums":"skipped (streaming dataset)",
            "start_time":download_start,
            "dataset_card":readme,
            "end_time":None
        }

    def download_dataset_card(self, source_config, save_dir):
        dataset_name = source_config["hf_name"]
        config = source_config.get("config") or "default"
        split = source_config["split"]

        safe_dataset = dataset_name.replace("/", "_")

        target_path = os.path.join(
            save_dir,
            f"{safe_dataset}_{config}_{split}_README.md"
        )

        try:
            readme_path = hf_hub_download(
                repo_id=dataset_name,
                filename="README.md",
                repo_type="dataset"
            )
        except Exception:
            return None

        with open(readme_path, "r", encoding="utf-8") as src:
            with open(target_path, "w", encoding="utf-8") as dst:
                dst.write(src.read())

        return target_path

    def flush(self, source_config, save_dir):
        raw_info = self.raw_info(source_config, save_dir)
        os.makedirs(save_dir, exist_ok=True)

        raw_info = self.raw_info(source_config, save_dir)

        dataset_name = source_config["hf_name"].replace("/", "_")
        config = source_config.get("config") or "default"
        split = source_config["split"]

        metadata_path = os.path.join(
            save_dir,
            f"{dataset_name}_{config}_{split}_raw_metadata.json"
        )

        with open(metadata_path, "w", encoding="utf-8") as f:
            json.dump(raw_info, f, indent=2)

        return metadata_path
