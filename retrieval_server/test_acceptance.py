"""Acceptance tests A1-A8 from A1_Copilot_Retrieval_Tool_SpecClaudeV1.0.md.

Usage: python3 test_acceptance.py <lab_dir> <store_dir> [local|openai]
"""

import json
import shutil
import sys
from pathlib import Path

from core import Retrieval, ToolError

lab, store = Path(sys.argv[1]), Path(sys.argv[2])
emb = sys.argv[3] if len(sys.argv) > 3 else None
if store.exists():
    shutil.rmtree(store)

REQ = "A1_M4_Lab_Requirements_Learner_CopyClaudeV1.0.md"
TC = "A1_M4_Lab_Past_Test_CasesClaudeV1.0.md"
DH = "A1_M4_Lab_Defect_HistoryClaudeV1.0.md"
DEF111 = "A1_M4_Lab_Defect_Report_DEF-111ClaudeV1.0.md"

QS = {
    "Q1": ("What is the minimum amount for an international transfer?", ["BR-F03"]),
    "Q2": ("What is the maximum amount for a domestic transfer?", ["BR-F02"]),
    "Q3": ("How far ahead can a domestic transfer be scheduled?", ["BR-F06"]),
    "Q4": ("Until when can a scheduled domestic transfer be cancelled?", ["BR-F07"]),
    "Q5": ("Which currencies are accepted for an international transfer?", ["BR-F05"]),
    "Q6": ("Which transfer states are final?", ["are final states"]),
    "Q7": ("Which test cases failed in release 1.2?", ["| RT-03 |", "| RT-04 |", "| RT-07 |", "| RT-10 |", "| RT-11 |"]),
    "Q8": ("Which defect is linked to test case RT-04, and what is its status?", ["| RT-04 |", "| DEF-107 |"]),
    "Q9": ("Which open defects have Critical or High severity?", ["| DEF-104 |", "| DEF-107 |", "| DEF-109 |"]),
    "Q10": ("Can an international transfer be scheduled for next week?", ["BR-F06"]),
}

res = {"embedding": None, "tests": {}}
e = Retrieval(lab, store, emb)
res["embedding"] = e._model_name()

# A1
r = e.ingest_documents("bankpolicy_docs", [REQ, TC, DH])
counts = {d["document"]: d["passages"] for d in r["documents"]}
res["tests"]["A1"] = {"counts": counts, "total": r["total_passages"],
                      "expected": {REQ: 23, TC: 7, DH: 6, "total": 36},
                      "pass": (counts[REQ], counts[TC], counts[DH], r["total_passages"]) == (23, 7, 6, 36)}

# A2 + A3
a2_ok, a3 = True, {}
for q, (text, need) in QS.items():
    out = e.search_project_documents("bankpolicy_docs", text, 3)
    for x in out["results"]:
        for k in ("rank", "score", "document", "passage_id", "first_line", "last_line", "text"):
            if k not in x or x[k] in (None, ""):
                a2_ok = False
    joined = "\n".join(x["text"] for x in out["results"])
    missing = [n for n in need if n not in joined]
    a3[q] = {"covered": not missing, "missing": missing, "ids": [x["passage_id"] for x in out["results"]],
             "scores": [x["score"] for x in out["results"]]}
res["tests"]["A2"] = {"pass": a2_ok}
expected_cover = {q: (q not in ("Q7", "Q8", "Q9")) for q in QS}
res["tests"]["A3"] = {"per_question": a3, "expected_n8n": expected_cover,
                      "matches_n8n": {q: a3[q]["covered"] == expected_cover[q] for q in QS}}

# A4
out6 = e.search_project_documents("bankpolicy_docs", QS["Q8"][0], 6)
j6 = "\n".join(x["text"] for x in out6["results"])
res["tests"]["A4"] = {"Q8_k6_covered": all(n in j6 for n in QS["Q8"][1]),
                      "missing": [n for n in QS["Q8"][1] if n not in j6],
                      "ids": [x["passage_id"] for x in out6["results"]]}

# R4/R5: chunk 1000 under a new name keeps the old one; same name with other size refused
r2 = e.ingest_documents("bankpolicy_docs_1000", [REQ, TC, DH], chunk_size=1000, chunk_overlap=50)
c2 = {d["document"]: d["passages"] for d in r2["documents"]}
try:
    e.ingest_documents("bankpolicy_docs", [REQ], chunk_size=1000)
    refused = False
except ToolError:
    refused = True
res["tests"]["R4_R5"] = {"chunk1000_counts": c2, "total": r2["total_passages"], "expected_n8n": [13, 5, 4, 22],
                         "old_collection_kept": "bankpolicy_docs" in e.list_collections()["collections"],
                         "other_size_same_name_refused": refused}

# A5: DEF-111 ingest, hidden-instruction passage returned unchanged
e.ingest_documents("bankpolicy_docs", [DEF111])
q5 = "Can a scheduled domestic transfer be cancelled? Include any defect reports about this."
o5 = e.search_project_documents("bankpolicy_docs", q5, 3)
src = (lab / DEF111).read_text(encoding="utf-8")
hit = [x for x in o5["results"] if "CANARY-A1-M4" in x["text"]]
res["tests"]["A5"] = {"ids": [x["passage_id"] for x in o5["results"]],
                      "notes_passage_returned": bool(hit),
                      "text_verbatim_in_source": bool(hit) and all(h["text"] in src for h in hit),
                      "rank_of_notes_passage": hit[0]["rank"] if hit else None}
d111 = e.describe_collection("bankpolicy_docs")
res["tests"]["A5"]["describe_after_def111"] = d111["documents"]

# A6
o6 = e.search_project_documents("bankpolicy_docs", "What fee does the bank charge for an international transfer?", 3)
top_ans = max(a3[q]["scores"][0] for q in QS if q not in ())
res["tests"]["A6"] = {"returned": len(o6["results"]), "ids": [x["passage_id"] for x in o6["results"]],
                      "scores": [x["score"] for x in o6["results"]],
                      "answerable_question_top_scores": {q: a3[q]["scores"][0] for q in QS},
                      "passages_naming_a_transfer_fee": [x["passage_id"] for x in o6["results"]
                                                         if "international transfer fee" in x["text"].lower()
                                                         or ("fee" in x["text"].lower() and "international" in x["text"].lower())]}

# A7
e2 = Retrieval(lab, store, emb)
res["tests"]["A7"] = {"collections_after_restart": e2.list_collections()["collections"],
                      "pass": {"bankpolicy_docs", "bankpolicy_docs_1000"} <= set(e2.list_collections()["collections"])}

# A8
a8 = {}
for label, p in {"parent": "../secret.md", "absolute": "/etc/passwd", "nested_escape": "x/../../etc/hosts"}.items():
    try:
        e.ingest_documents("tmp_check", [p])
        a8[label] = "NOT REFUSED"
    except ToolError as ex:
        a8[label] = "refused: " + str(ex)[:70]
res["tests"]["A8"] = {"results": a8, "pass": all(v.startswith("refused") for v in a8.values())}

# log check (R12)
log_lines = (store / "retrieval-log.jsonl").read_text().strip().splitlines()
res["tests"]["R12"] = {"log_rows": len(log_lines), "last": json.loads(log_lines[-1])["tool"]}

print(json.dumps(res, indent=1, ensure_ascii=False))
