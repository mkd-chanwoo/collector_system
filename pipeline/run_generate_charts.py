import os
import json
import matplotlib.pyplot as plt
from datetime import datetime

BASE_DIR = "evidence/charts"
os.makedirs(BASE_DIR, exist_ok=True)

HISTORY_PATH = "state/history.jsonl"
SNAPSHOT_PATH = "checkpoints/pipeline_checkpoint.json"


# =========================
# load
# =========================
def load_history():
    data = []
    with open(HISTORY_PATH, "r") as f:
        for line in f:
            data.append(json.loads(line))
    return data


def load_snapshot():
    if not os.path.exists(SNAPSHOT_PATH):
        return None
    with open(SNAPSHOT_PATH) as f:
        return json.load(f)


def save(name):
    plt.tight_layout()
    plt.savefig(f"{BASE_DIR}/{name}.png")
    plt.clf()


# =========================
# 1. Token count by source
# =========================
def token_by_source(history):
    source_tokens = {}

    for h in history:
        src = h["dataset"]
        tok = h.get("total_tokens", 0)
        source_tokens[src] = max(source_tokens.get(src, 0), tok)

    plt.bar(source_tokens.keys(), source_tokens.values())
    plt.title("Token Count by Source")
    save("token_by_source")


# =========================
# 2. Token count by domain
# =========================
def token_by_domain(snapshot):
    domain_tokens = snapshot["quota_state"]["domain_tokens"]

    plt.bar(domain_tokens.keys(), domain_tokens.values())
    plt.title("Token Count by Domain")
    save("token_by_domain")


# =========================
# 3. Cumulative tokens
# =========================
def cumulative_tokens(history):
    tokens = [h["total_tokens"] for h in history]

    plt.plot(tokens)
    plt.title("Cumulative Tokens")
    save("cumulative_tokens")


# =========================
# 4. Cleaned vs raw
# =========================
def cleaned_vs_raw(snapshot):
    stats = snapshot["stats_tmp"]

    raw = stats["documents"]
    cleaned = raw - (
        stats["quality"] +
        stats["lang_confi"] +
        stats["lang_in"] +
        stats["dedup_exact"] +
        stats["dedup_near"] +
        stats["toxic"]
    )

    plt.bar(["raw", "cleaned"], [raw, cleaned])
    plt.title("Cleaned vs Raw")
    save("cleaned_vs_raw")


# =========================
# 5. Dedup impact
# =========================
def dedup_impact(snapshot):
    stats = snapshot["stats_tmp"]

    values = {
        "exact": stats["dedup_exact"],
        "near": stats["dedup_near"]
    }

    plt.bar(values.keys(), values.values())
    plt.title("Deduplication Impact")
    save("dedup_impact")


# =========================
# 6. Document length distribution
# =========================
def doc_length_dist(history):
    lengths = []

    for h in history:
        s = h["stats_tmp"]
        lengths.append(s.get("documents", 0))

    plt.hist(lengths, bins=20)
    plt.title("Document Length Distribution")
    save("doc_length_distribution")


# =========================
# 7. Token length distribution
# =========================
def token_length_dist(history):
    tokens = [h["total_tokens"] for h in history]

    plt.hist(tokens, bins=20)
    plt.title("Token Length Distribution")
    save("token_length_distribution")


# =========================
# 8. Language purity
# =========================
def language_purity(snapshot):
    stats = snapshot["stats_tmp"]

    total = stats["documents"]
    bad = stats["lang_confi"] + stats["lang_in"]
    good = total - bad

    plt.pie([good, bad], labels=["valid", "invalid"], autopct="%1.1f%%")
    plt.title("Language Purity")
    save("language_purity")


# =========================
# 9. Daily throughput
# =========================
def daily_throughput(history):
    date_tokens = {}

    for h in history:
        t = h["timestamp"][:10]
        date_tokens.setdefault(t, 0)
        date_tokens[t] = max(date_tokens[t], h["total_tokens"])

    dates = sorted(date_tokens.keys())
    values = [date_tokens[d] for d in dates]

    plt.plot(dates, values)
    plt.xticks(rotation=45)
    plt.title("Daily Throughput")
    save("daily_throughput")


# =========================
# 10. Audit pass/fail
# =========================
def audit_summary(snapshot):
    stats = snapshot["stats_tmp"]

    passed = stats["documents"] - stats["audit"]
    failed = stats["audit"]

    plt.bar(["pass", "fail"], [passed, failed])
    plt.title("Audit Summary")
    save("audit_summary")


# =========================
# 11. Storage growth
# =========================
def storage_growth(history):
    sizes = [h["total_tokens"] * 4 for h in history]

    plt.plot(sizes)
    plt.title("Storage Growth")
    save("storage_growth")


# =========================
# main
# =========================
def main():
    print("Generating charts from state...")

    history = load_history()
    snapshot = load_snapshot()

    token_by_source(history)
    token_by_domain(snapshot)
    cumulative_tokens(history)
    cleaned_vs_raw(snapshot)
    dedup_impact(snapshot)
    doc_length_dist(history)
    token_length_dist(history)
    language_purity(snapshot)
    daily_throughput(history)
    audit_summary(snapshot)
    storage_growth(history)

    print("All charts saved to evidence/charts/")


if __name__ == "__main__":
    main()