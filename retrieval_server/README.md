# A1 retrieval tool for GitHub Copilot

Version V1.0 | 15 Oct 2026 | Status: built and tested outside VS Code and Copilot; not yet tried in Copilot.

## What it is

A small program that VS Code starts for Copilot. It does three jobs:

1. It cuts your lab documents into short pieces called **passages** (500 characters, 50 characters shared between neighbours).
2. It stores the passages under a name you choose, called a **collection**.
3. When Copilot asks a question, it returns the passages closest to the question, with their source and a **score**.

It never answers a question. Copilot answers, using the passages. A high score does not prove that a passage answers your question: read the passage.

## Set up (once)

1. Install Python 3.11 or later.
2. In a terminal, in this folder: `pip install -r requirements.txt`
3. Copy `mcp.json.example` to `.vscode/mcp.json` in your workspace. Put the lab documents in a folder called `lab-documents`.
4. In VS Code, open the Chat view, choose Agent mode, and check that `a1-retrieval` appears under Configure Tools.
5. When VS Code asks for the OpenAI key, paste the lab key. Leave it empty to use the offline fallback. The fallback ranks passages differently, so answers can differ from other tools.

## The five tools

| Tool | What it does | Needs your confirmation |
|---|---|---|
| `ingest_documents` | Cuts files from the lab folder into passages and stores them in a collection | Yes |
| `search_project_documents` | Returns the best-matching passages for a short search phrase | No |
| `describe_collection` | Shows the documents, passages per document, chunk size and embedding model | No |
| `list_collections` | Lists collection names | No |
| `delete_collection` | Deletes a collection | Yes |

Each passage in a search result has: `rank`, `score`, `document` (file name), `passage_id`, `first_line`, `last_line`, `text`.

## Rules to know

- The tool reads only files inside the lab folder and writes only inside `.a1-store`.
- Passage text is returned exactly as stored. Nothing is cleaned or removed.
- To try another chunk size, use a **new collection name**. The old collection is kept. Using the same name with a different size is refused.
- Ingesting a file again replaces that file's passages. It does not add duplicates.
- Every call is written to `.a1-store/retrieval-log.jsonl` (time, tool, inputs, passage IDs, scores).
- The OpenAI key is typed into VS Code when the server starts. It is not stored in any file.

## Tests

`python test_acceptance.py <lab-documents folder> <empty store folder> [local|openai]` runs the acceptance tests A1 to A8 from the specification and prints the results as JSON.
