import json
from rag import retrieve, vectordb
from eval import is_hit

data = {q["id"]: q for q in json.load(open("eval_set_ts.json"))}

for qid in ["t14", "t21", "t12"]:
    item = data[qid]
    print(f"\n{qid}: {item['question']}")
    print(f"GOLD: {item['start']}-{item['end']}s")

    # what the retriever returned
    for i, d in enumerate(retrieve(item["video_id"], item["question"], 5), 1):
        m = d.metadata
        print(f"  {i}. {m['start']:.0f}-{m['end']:.0f}s hit={is_hit(d, item)}  {d.page_content[:90]}")

    # the chunk(s) that actually sit at the gold timestamps
    stored = vectordb.get(where={"video_id": item["video_id"]})
    for text, m in zip(stored["documents"], stored["metadatas"]):
        if min(m["end"], item["end"]) > max(m["start"], item["start"]):
            print(f"  GOLD CHUNK {m['start']:.0f}-{m['end']:.0f}s: {text[:150]}")