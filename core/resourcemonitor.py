import psutil
import subprocess


class ResourceMonitor:

    def __init__(self):
        self.process = psutil.Process()

    def get_cpu_ram(self):
        cpu = psutil.cpu_percent(interval=None)
        mem = psutil.virtual_memory()

        return {
            "cpu_percent": cpu,
            "ram_percent": mem.percent,
            "ram_used_gb": round(mem.used / (1024**3), 2)
        }

    def get_gpu(self):
        """
        nvidia-smi 기반 GPU 정보
        """
        try:
            result = subprocess.check_output(
                [
                    "nvidia-smi",
                    "--query-gpu=utilization.gpu,memory.used,memory.total",
                    "--format=csv,noheader,nounits"
                ],
                encoding="utf-8"
            )

            gpu_stats = []
            for line in result.strip().split("\n"):
                util, mem_used, mem_total = line.split(", ")
                gpu_stats.append({
                    "gpu_util_percent": int(util),
                    "gpu_mem_used_mb": int(mem_used),
                    "gpu_mem_total_mb": int(mem_total)
                })

            return gpu_stats

        except Exception:
            return []

    def get_stats(self):
        stats = self.get_cpu_ram()
        gpu = self.get_gpu()

        if gpu:
            stats["gpu"] = gpu

        return stats

    def log(self, prefix="RESOURCE"):
        stats = self.get_stats()

        msg = (
            f"[{prefix}] CPU={stats['cpu_percent']}% | "
            f"RAM={stats['ram_percent']}% ({stats['ram_used_gb']}GB)"
        )

        if "gpu" in stats:
            for i, g in enumerate(stats["gpu"]):
                msg += (
                    f" | GPU{i}: {g['gpu_util_percent']}% "
                    f"({g['gpu_mem_used_mb']}/{g['gpu_mem_total_mb']} MB)"
                )

        print(msg)

        return stats