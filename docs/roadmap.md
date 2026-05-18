# Corpus Forge Roadmap

## Purpose
This document captures the current application structure and the planned path for adding ChromaDB and generative AI features without turning `app.py` into a merge-conflict hotspot.

## Current Structure
- `app.py` is the bootstrap file.
- `routes/ingestion.py` owns upload, delete, index, and active-corpus selection.
- `routes/chat.py` is reserved for future chat and AI workflows.
- `extractor.py` handles text extraction from uploaded files.
- The selected corpus is stored per user in Flask session state under `active_corpus`.

## Near-Term Plan
### 1. Keep routing separated with Blueprints
- Keep ingestion and chat in separate blueprint modules.
- Add new routes only to the blueprint that owns the feature.
- Keep shared config and blueprint registration in `app.py`.

### 2. Add a ChromaDB service layer
- Create a dedicated module for vector store setup and access.
- Store embedding creation, collection management, and similarity search outside the route handlers.
- Have routes call the service layer instead of talking to ChromaDB directly.

### 3. Add generative AI orchestration
- Keep prompt building, retrieval, and response formatting in a separate chat service module.
- Use the active corpus as the source of documents for retrieval.
- Keep chat routes thin: receive the request, call the service, render the response.

## Suggested File Layout
```text
app.py
extractor.py
routes/
  __init__.py
  ingestion.py
  chat.py
services/
  chroma_service.py
  chat_service.py
  embedding_service.py
templates/
  index.html
  chat.html
```

## Implementation Phases
### Phase 1: Stabilize the current app
- Keep the ingestion blueprint clean.
- Keep session-backed active corpus selection working.
- Keep delete and upload validation centralized.

### Phase 2: Add embeddings and indexing
- Generate embeddings from extracted text after upload.
- Persist chunks and metadata in ChromaDB.
- Map each chunk back to its source filename.

### Phase 3: Add retrieval-augmented chat
- Read the user’s `active_corpus` from session.
- Retrieve relevant chunks from ChromaDB.
- Build a grounded prompt and call the model.

### Phase 4: Improve collaboration safety
- Add unit tests around blueprint routes and service functions.
- Keep route changes isolated to one blueprint per feature area.
- Avoid cross-file edits unless a change is truly shared.

## Team Guidance
- Put domain-specific code in blueprints or services, not in `app.py`.
- Use shared helpers only for shared concerns such as filename validation and extraction.
- Treat `active_corpus` as user-specific session data, not global state.
- Keep future AI logic behind service interfaces so model/provider changes stay localized.
