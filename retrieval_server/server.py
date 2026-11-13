"""A1 retrieval tool - MCP server (stdio).

Start it from VS Code with a workspace mcp.json (see README.md). It offers five tools.
Environment: A1_LAB_DIR (folder the tool may read), A1_STORE_DIR (folder it writes to),
OPENAI_API_KEY (optional), A1_EMBEDDING (openai or local).
"""

from __future__ import annotations

import os
import sys

from mcp.server.mcpserver import MCPServer
from mcp.server.mcpserver.exceptions import ToolError as McpToolError

from core import Retrieval, ToolError

lab_dir = os.environ.get("A1_LAB_DIR") or os.getcwd()
store_dir = os.environ.get("A1_STORE_DIR") or os.path.join(os.getcwd(), ".a1-retrieval-store")
engine = Retrieval(lab_dir, store_dir)

server = MCPServer("a1-retrieval", instructions=(
    "Searches BankPolicy lab documents. It returns passages with their source and a score. "
    "It does not answer questions. A high score does not prove that a passage answers the question: read the passage."))


def _guard(fn, *a, **k):
    try:
        return fn(*a, **k)
    except ToolError as e:
        raise McpToolError(str(e)) from None


@server.tool()
def ingest_documents(collection: str, files: list[str], chunk_size: int = 500, chunk_overlap: int = 50) -> dict:
    """Split lab documents into passages and store them in a collection. Files are names inside the lab folder."""
    return _guard(engine.ingest_documents, collection, files, chunk_size, chunk_overlap)


@server.tool()
def search_project_documents(collection: str, query: str, top_k: int = 3) -> dict:
    """Return the passages that best match a short search phrase: rank, score, document, passage ID, lines, text."""
    return _guard(engine.search_project_documents, collection, query, top_k)


@server.tool()
def describe_collection(collection: str) -> dict:
    """Show the documents, passages per document, chunk size, overlap and embedding model of a collection."""
    return _guard(engine.describe_collection, collection)


@server.tool()
def list_collections() -> dict:
    """List the collection names."""
    return engine.list_collections()


@server.tool()
def delete_collection(collection: str) -> dict:
    """Delete a collection."""
    return _guard(engine.delete_collection, collection)


if __name__ == "__main__":
    print(f"a1-retrieval: embedding={engine.embedding} model={engine._model_name()}", file=sys.stderr)
    server.run()
