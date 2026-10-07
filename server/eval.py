import json
from collections import defaultdict
from rag import retrieve

def is_hit(doc, gold):
    overlap = min(doc.metadata["end"], gold["end"]) - max(doc.metadata["start"], gold["start"])
    return overlap >= min(3, 0.5 * (gold["end"] - gold["start"]))

def evaluate(path, k=5):
    data = json.load(open(path))
    hits, rr_total = 0, 0.0
    by_type = defaultdict(lambda: [0, 0])  # type -> [hits, total]

    for item in data:
        docs = retrieve(item["video_id"], item["question"], k)
        rank = next((i + 1 for i, d in enumerate(docs) if is_hit(d, item)), None)

        by_type[item["type"]][1] += 1
        if rank:
            hits += 1
            rr_total += 1 / rank
            by_type[item["type"]][0] += 1
        else:
            print(f"MISS {item['id']}: {item['question']}")

    print(f"\nk={k}  Hit@k: {hits/len(data):.1%}  MRR: {rr_total/len(data):.3f}")
    for t, (h, n) in by_type.items():
        print(f"  {t}: {h}/{n}")

if __name__ == "__main__":
    for path in ("eval_set.json", "eval_set_ts.json"):
        print(f"\n=== {path} ===")
        for k in (1, 3, 5):
            evaluate(path, k)