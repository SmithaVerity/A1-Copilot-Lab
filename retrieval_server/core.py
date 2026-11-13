"""A1 retrieval tool - core logic (no MCP code here, so it can be tested on its own).

Stores documents as passages, finds the passages closest to a question, and returns them
verbatim with their source. It never answers questions and never cleans passage text.
"""

from __future__ import annotations

import json
import os
import re
import time
import urllib.request
from pathlib import Path

from langchain_text_splitters import RecursiveCharacterTextSplitter

DEFAULT_CHUNK_SIZE = 500
DEFAULT_CHUNK_OVERLAP = 50
DEFAULT_TOP_K = 3
OPENAI_MODEL = "text-embedding-3-small"
LOCAL_MODEL = "local-tfidf (offline fallback, ranks differ from OpenAI)"

_NAME_OK = re.compile(r"^[A-Za-z0-9_\-]{1,64}$")


class ToolError(Exception):
    """A problem the learner can read and act on."""


class Retrieval:
    def __init__(self, lab_dir: str | Path, store_dir: str | Path, embedding: str | None = None):
        self.lab_dir = Path(lab_dir).resolve()
        self.store_dir = Path(store_dir).resolve()
        self.store_dir.mkdir(parents=True, exist_ok=True)
        self.log_path = self.store_dir / "retrieval-log.jsonl"
        wanted = (embedding or os.environ.get("A1_EMBEDDING") or "").lower()
        if wanted == "openai" and not os.environ.get("OPENAI_API_KEY"):
            raise ToolError("A1_EMBEDDING=openai needs OPENAI_API_KEY to be set.")
        if wanted in ("openai", "local"):
            self.embedding = wanted
        else:
            self.embedding = "openai" if os.environ.get("OPENAI_API_KEY") else "local"

    # ---------------------------------------------------------------- helpers
    def _model_name(self) -> str:
        return OPENAI_MODEL if self.embedding == "openai" else LOCAL_MODEL

    def _coll_path(self, name: str) -> Path:
        if not _NAME_OK.match(name or ""):
            raise ToolError("Collection names use letters, digits, '_' and '-' only (1 to 64 characters).")
        return self.store_dir / f"{name}.json"

    def _load(self, name: str) -> dict:
        p = self._coll_path(name)
        if not p.exists():
            raise ToolError(f"Collection '{name}' does not exist. Collections: {self.list_collections()['collections']}")
        return json.loads(p.read_text(encoding="utf-8"))

    def _save(self, name: str, data: dict) -> None:
        self._coll_path(name).write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")

    def _log(self, tool: str, inputs: dict, result: dict) -> None:
        row = {"time": time.strftime("%Y-%m-%dT%H:%M:%S"), "tool": tool, "inputs": inputs}
        if "results" in result:
            row["passages"] = [{"id": r["passage_id"], "score": r["score"]} for r in result["results"]]
        with self.log_path.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(row, ensure_ascii=False) + "\n")

    def _resolve_in_lab(self, rel: str) -> Path:
        p = (self.lab_dir / rel).resolve()
        if p != self.lab_dir and self.lab_dir not in p.parents:
            raise ToolError(f"Refused: '{rel}' is outside the lab folder. Only files inside the lab folder can be read.")
        if not p.is_file():
            raise ToolError(f"File not found in the lab folder: '{rel}'.")
        return p

    # -------------------------------------------------------------- embedding
    def _embed_openai(self, texts: list[str]) -> list[list[float]]:
        out: list[list[float]] = []
        for i in range(0, len(texts), 96):
            batch = texts[i : i + 96]
            req = urllib.request.Request(
                "https://api.openai.com/v1/embeddings",
                data=json.dumps({"model": OPENAI_MODEL, "input": batch}).encode(),
                headers={
                    "Authorization": f"Bearer {os.environ['OPENAI_API_KEY']}",
                    "Content-Type": "application/json",
                },
            )
            with urllib.request.urlopen(req, timeout=60) as r:
                body = json.loads(r.read())
            out.extend(d["embedding"] for d in sorted(body["data"], key=lambda d: d["index"]))
        return out

    @staticmethod
    def _cosine(a: list[float], b: list[float]) -> float:
        import numpy as np

        va, vb = np.asarray(a), np.asarray(b)
        d = float(np.linalg.norm(va) * np.linalg.norm(vb))
        return float(va @ vb / d) if d else 0.0

    def _scores(self, coll: dict, query: str) -> list[float]:
        texts = [p["text"] for p in coll["passages"]]
        if coll["embedding"] == "openai":
            qv = self._embed_openai([query])[0]
            return [self._cosine(qv, p["vector"]) for p in coll["passages"]]
        from sklearn.feature_extraction.text import TfidfVectorizer
        from sklearn.metrics.pairwise import cosine_similarity

        vec = TfidfVectorizer(lowercase=True, ngram_range=(1, 2), sublinear_tf=True, token_pattern=r"(?u)\b[\w\-\.]+\b")
        m = vec.fit_transform(texts + [query])
        return [float(x) for x in cosine_similarity(m[-1], m[:-1])[0]]

    # ------------------------------------------------------------------ tools
    @staticmethod
    def split(text: str, size: int, overlap: int) -> list[dict]:
        """Recursive character splitter (paragraph, line, space), as the n8n lab uses."""
        splitter = RecursiveCharacterTextSplitter(chunk_size=size, chunk_overlap=overlap)
        chunks = splitter.split_text(text)
        out, cursor = [], 0
        for c in chunks:
            idx = text.find(c, max(0, cursor - overlap - 5))
            if idx < 0:
                idx = text.find(c)
            if idx < 0:
                idx = cursor
            start_line = text.count("\n", 0, idx) + 1
            end_line = start_line + c.count("\n")
            out.append({"text": c, "start_line": start_line, "end_line": end_line})
            cursor = idx + len(c)
        return out

    def ingest_documents(self, collection: str, files: list[str], chunk_size: int = DEFAULT_CHUNK_SIZE,
                         chunk_overlap: int = DEFAULT_CHUNK_OVERLAP) -> dict:
        if chunk_size < 50 or chunk_size > 5000:
            raise ToolError("chunk_size must be between 50 and 5000 characters.")
        if chunk_overlap < 0 or chunk_overlap >= chunk_size:
            raise ToolError("chunk_overlap must be 0 or more and smaller than chunk_size.")
        if not files:
            raise ToolError("Give at least one file name from the lab folder.")
        path = self._coll_path(collection)
        coll = json.loads(path.read_text(encoding="utf-8")) if path.exists() else {
            "collection": collection, "chunk_size": chunk_size, "chunk_overlap": chunk_overlap,
            "embedding": self.embedding, "model": self._model_name(), "passages": [], "ingested": [],
        }
        if path.exists() and (coll["chunk_size"], coll["chunk_overlap"]) != (chunk_size, chunk_overlap):
            raise ToolError(
                f"Collection '{collection}' already uses chunk_size {coll['chunk_size']} / overlap {coll['chunk_overlap']}. "
                "To try other sizes, use a new collection name (the old one is kept)."
            )
        per_doc = []
        for rel in files:
            p = self._resolve_in_lab(rel)
            text = p.read_text(encoding="utf-8")
            coll["passages"] = [x for x in coll["passages"] if x["document"] != p.name]  # re-ingest replaces
            pieces = self.split(text, chunk_size, chunk_overlap)
            new = []
            for n, piece in enumerate(pieces, 1):
                new.append({
                    "passage_id": f"{p.name}#{n}", "document": p.name, "start_line": piece["start_line"],
                    "end_line": piece["end_line"], "text": piece["text"], "vector": None,
                })
            coll["passages"].extend(new)
            per_doc.append({"document": p.name, "passages": len(new)})
        if coll["embedding"] == "openai":
            todo = [x for x in coll["passages"] if x["vector"] is None]
            for x, v in zip(todo, self._embed_openai([x["text"] for x in todo])):
                x["vector"] = v
        coll["ingested"] = sorted({x["document"] for x in coll["passages"]})
        coll["date"] = time.strftime("%Y-%m-%d %H:%M")
        self._save(collection, coll)
        result = {"collection": collection, "documents": per_doc, "total_passages": len(coll["passages"]),
                  "chunk_size": chunk_size, "chunk_overlap": chunk_overlap, "embedding_model": coll["model"]}
        self._log("ingest_documents", {"collection": collection, "files": files, "chunk_size": chunk_size,
                                       "chunk_overlap": chunk_overlap}, result)
        return result

    def search_project_documents(self, collection: str, query: str, top_k: int = DEFAULT_TOP_K) -> dict:
        if not (query or "").strip():
            raise ToolError("Give a search phrase.")
        if top_k < 1 or top_k > 20:
            raise ToolError("top_k must be between 1 and 20.")
        coll = self._load(collection)
        scores = self._scores(coll, query)
        order = sorted(range(len(scores)), key=lambda i: -scores[i])[:top_k]
        results = []
        for rank, i in enumerate(order, 1):
            p = coll["passages"][i]
            results.append({"rank": rank, "score": round(scores[i], 4), "document": p["document"],
                            "passage_id": p["passage_id"], "first_line": p["start_line"],
                            "last_line": p["end_line"], "text": p["text"]})
        out = {"collection": collection, "query": query, "top_k": top_k, "embedding_model": coll["model"],
               "results": results}
        self._log("search_project_documents", {"collection": collection, "query": query, "top_k": top_k}, out)
        return out

    def describe_collection(self, collection: str) -> dict:
        coll = self._load(collection)
        per: dict[str, int] = {}
        for p in coll["passages"]:
            per[p["document"]] = per.get(p["document"], 0) + 1
        out = {"collection": collection, "documents": [{"document": d, "passages": n} for d, n in sorted(per.items())],
               "total_passages": len(coll["passages"]), "chunk_size": coll["chunk_size"],
               "chunk_overlap": coll["chunk_overlap"], "embedding_model": coll["model"], "last_ingest": coll.get("date")}
        self._log("describe_collection", {"collection": collection}, out)
        return out

    def list_collections(self) -> dict:
        names = sorted(p.stem for p in self.store_dir.glob("*.json"))
        return {"collections": names}

    def delete_collection(self, collection: str) -> dict:
        p = self._coll_path(collection)
        if not p.exists():
            raise ToolError(f"Collection '{collection}' does not exist.")
        p.unlink()
        self._log("delete_collection", {"collection": collection}, {})
        return {"deleted": collection}
