# Corpus Forge Project

An enterprise-grade, localized **Retrieval-Augmented Generation (RAG)** platform designed to parse, index, and query text, code, and document assets within a completely sandboxed workspace ecosystem. Built using Flask blueprints for highly decoupled scalability and featuring a persistent local vector store synchronized with the Google Gemini API.

---

## 🏗️ System Architecture & Modular Design

Corpus Forge is structurally engineered using a **Modular Layered Architecture** powered by Flask Blueprints. This layout ensures that distinct feature boundaries remain isolated, eliminating global state vulnerabilities and allowing developers to scale features simultaneously without encountering source-control merge conflicts.


```

capstone-corpus-forge/
├── data/                       # Sandboxed local host file uploads
├── chroma_db/                  # Persistent binary vector storage tables
├── logs/                       # Application operation audit trails
├── routes/                     # Decoupled Blueprint endpoints
│   ├── **init**.py
│   ├── ingestion.py            # File processing and deletion logic
│   └── chat.py                 # Vector querying and Gemini SDK integration
├── static/                     # Modular frontend assets
│   ├── css/
│   │   └── chat.css            # Production-grade UI styling sheets
│   └── js/
│       └── chat.js             # Asynchronous DOM/fetch context handlers
├── templates/                  # Structural markup layouts
│   ├── index.html              # Corpus management interface
│   └── chat.html               # Semantic conversation dashboard
├── app.py                      # Application bootstrap and global config
├── extractor.py                # Asset text compilation engine
├── utils.py                    # Independent security/validation helpers
├── vector_store.py             # ChromaDB index orchestrator class
└── requirements.txt            # Explicit dependency pinning

```

---

## 🔒 Enterprise Security Guardrails & Ingestion Pipeline

To protect the underlying infrastructure against malicious actors or accidental system resource exhaustion, Corpus Forge enforces strict boundary constraints at every point of execution:

1. **Content Verification (Magic Number Auditing):** Rather than validating extensions using insecure string methods (`.endswith()`), the ingestion engine leverages `python-magic` to parse the file header's true MIME-type signatures directly from the first 512 bytes of data.
2. **Defensive Path Traversal Mitigation:** The core file deletion layer sanitizes all runtime inputs using `os.path.abspath` combined with `os.path.commonpath` constraints. This forms an immutable boundary wall that ensures a user cannot navigate out of the local storage directory via token injection attacks (e.g., `../../etc/passwd`).
3. **Strict Memory & Allocation Limits:** The system intercepts multi-part file uploads at the middleware level, enforcing a rigid `MAX_FILE_SIZE` ceiling of **10MB** to maintain strict memory allocations on the hosting server.

---

## 📐 Algorithmic Chunking & Semantic Indexing

When documents are ingested, they pass through a sliding-window chunking sequence inside `vector_store.py`:
* **Fixed-size Structural Splitting:** Document data is systematically split into **1,000-character chunks** accompanied by a rolling **200-character semantic overlap** to preserve complete structural context across boundaries.
* **Session-State Isolation:** Rather than executing broad global queries, Corpus Forge passes specialized query metadata payloads into local **ChromaDB collections**, ensuring that vector matches are filtered strictly by the files actively pinned in the user's current `session['active_corpus']` array.

---

## 🛠️ Installation and Local Setup

### Prerequisites
* macOS / Linux / Windows system
* **Python 3.11+** installed
* **Homebrew** (for macOS system packages)

### 1. Install System Dependencies
The validation engine relies on `libmagic` to evaluate file binaries. Install it to your system paths:
```bash
# macOS
brew install libmagic

# Ubuntu/Debian
sudo apt-get install libmagic1

```

### 2. Configure Your Virtual Environment

Clone this project repository, navigate into the root workspace folder, and initialize an isolated execution loop:

```bash
cd capstone-corpus-forge
python3 -m venv .venv
source .venv/bin/activate

```

### 3. Synchronize Application Dependencies

Install the strictly pinned package tree contained within our configuration manifest:

```bash
pip install -r requirements.txt

```

### 4. Inject Cryptographic Credentials Securely

To protect proprietary security parameters, **never** hardcode API access tokens into the application files. Inject your key directly into temporary system memory space:

```bash
export GEMINI_API_KEY="your_secret_gemini_api_key_here"

```

---

## 🚀 Running the Application

Ensure your environment is fully activated and the environment variables are active in your current shell instance, then boot up the Flask development instance:

```bash
python app.py

```

Open your browser and navigate to the application dashboard:

```text
[http://127.0.0.1:5000](http://127.0.0.1:5000)

```

1. **Manage Files:** Upload source scripts (`.py`, `.js`), markdown logs (`.md`), plain texts (`.txt`), or documents (`.pdf`).
2. **Select Context:** Toggle the workspace checkboxes next to your ingested files and click **Save Active Corpus**.
3. **Talk to Documents:** Click **Go to AI Workspace Chat**, set your professional audience or prompt tone settings, and generate grounded answers immediately.

```

```


