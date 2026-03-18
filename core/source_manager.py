import yaml
import os


class SourceManager:
    """
    Manages dataset source registry.

    Responsibilities
    ----------------
    - Load dataset registry
    - Validate dataset configuration
    - Provide dataset metadata to pipeline
    """

    def __init__(self, config_path):

        if not os.path.exists(config_path):
            raise FileNotFoundError(f"Dataset config not found: {config_path}")

        with open(config_path, "r") as f:
            cfg = yaml.safe_load(f)

        if "datasets" not in cfg:
            raise ValueError("datasets.yaml must contain a 'datasets' section")

        self.sources = cfg["datasets"]

        self._validate_sources()

    def _validate_sources(self):
        """
        Validate dataset configuration
        """

        required_fields = [
            "hf_name",
            "config",
            "split",
            "field",
            "domain",
            "streaming",
            "target_tokens",
        ]

        for name, src in self.sources.items():

            for field in required_fields:
                if field not in src:
                    raise ValueError(
                        f"Dataset '{name}' missing required field '{field}'"
                    )

    def list_sources(self):
        """
        Return dictionary of all dataset sources
        """

        return self.sources

    def get_source(self, name):
        """
        Return single dataset config
        """

        if name not in self.sources:
            raise KeyError(f"Dataset '{name}' not found in registry")

        return self.sources[name]

    def print_summary(self):
        """
        Print dataset summary
        """

        print("\nRegistered datasets:\n")

        for name, src in self.sources.items():
            print(
                f"{name} | domain={src['domain']} | target_tokens={src['target_tokens']}"
            )

        print()