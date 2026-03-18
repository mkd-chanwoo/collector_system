import sys
from pathlib import Path


class TeeStream:

    def __init__(self, *streams):
        self.streams = streams

    def write(self, data):
        for s in self.streams:
            s.write(data)
            s.flush()

    def flush(self):
        for s in self.streams:
            s.flush()


def enable_file_logging(log_path):

    log_path = Path(log_path)
    log_path.parent.mkdir(parents=True, exist_ok=True)

    log_file = log_path.open("a", encoding="utf-8", buffering=1)

    sys.stdout = TeeStream(sys.stdout, log_file)
    sys.stderr = TeeStream(sys.stderr, log_file)