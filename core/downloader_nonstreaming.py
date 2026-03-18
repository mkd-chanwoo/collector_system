from datasets import load_dataset, DownloadConfig


class Downloader:
    def __init__(self):
        self.download_config = DownloadConfig(
            resume_download=True,
            max_retries=5
        )

    def load(self, source):
        hf_name = source.get("hf_name")
        config = source.get("config")
        split = source.get("split")

        if config in [None, "None"]:
            config = None
        if split in [None, "None"]:
            split = None

        dataset = load_dataset(
            hf_name,
            config,
            split=split,
            download_config=self.download_config
        )

        return dataset

    def materialize(self, dataset):
        """
        🔥 다운로드 강제 실행
        """
        return len(dataset)