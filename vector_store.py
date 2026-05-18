import os

# Disable ChromaDB telemetry to avoid Python 3.14 + protobuf incompatibility
os.environ["ANONYMIZED_TELEMETRY"] = "False"

try:
    import chromadb
    from chromadb.config import Settings
    from chromadb.utils import embedding_functions
except (ImportError, TypeError) as e:
    # Python 3.14+ has protobuf incompatibility with ChromaDB
    # This is a known issue; use Python 3.11 or 3.12 for production
    print(f"Warning: ChromaDB import failed: {e}")
    print("ChromaDB vector storage will not be available.")
    print("Please use Python 3.11 or 3.12 for full functionality.")
    chromadb = None
    Settings = None
    embedding_functions = None


class VectorStoreManager:
    def __init__(
        self,
        db_path: str = "chroma_db",
        collection_name: str = "corpus_forge_collection",
    ):
        """Initializes a persistent local ChromaDB client and collection."""
        if chromadb is None:
            self.client = None
            self.collection = None
            self.embedding_function = None
            return

        # Ensure the storage directory exists
        os.makedirs(db_path, exist_ok=True)

        # Initialize persistent client on your local machine
        # Explicitly disable anonymized telemetry to avoid posthog API mismatch noise.
        client_settings = Settings(anonymized_telemetry=False) if Settings else None
        self.client = chromadb.PersistentClient(path=db_path, settings=client_settings)

        # Use ChromeDB's default embedding function (all-MiniLM-L6-v2)
        self.embedding_function = embedding_functions.DefaultEmbeddingFunction()

        # Get or create the collection
        self.collection = self.client.get_or_create_collection(
            name=collection_name, embedding_function=self.embedding_function
        )

    def add_document(
        self, filename: str, text: str, chunk_size: int = 1000, chunk_overlap: int = 200
    ):
        """
        Splits a document's extracted text into overlapping chunks and stores them.
        Fulfills Layer 2 Challenge A: Fixed-size overlapping chunking strategy.
        """
        if self.collection is None:
            # ChromaDB unavailable; silently skip
            return

        if not text.strip():
            return

        # First, remove any existing chunks for this specific file to prevent duplicates
        self.collection.delete(where={"filename": filename})

        chunks = []
        metadata_list = []
        ids = []

        # Perform the fixed-size sliding window chunking
        start = 0
        chunk_idx = 0
        while start < len(text):
            end = start + chunk_size
            chunk = text[start:end]

            chunks.append(chunk)
            metadata_list.append({"filename": filename})
            ids.append(f"{filename}_chunk_{chunk_idx}")

            # Slide the window forward by chunk_size minus the overlap
            start += chunk_size - chunk_overlap
            chunk_idx += 1

        # Add the batch of chunks directly to ChromaDB
        if chunks:
            self.collection.add(documents=chunks, metadatas=metadata_list, ids=ids)

    def delete_document(self, filename: str) -> None:
        """Delete all chunks associated with a document.

        Args:
            filename: Name of the document to delete.
        """
        if self.collection is None:
            # ChromaDB unavailable; silently skip
            return

        try:
            self.collection.delete(where={"filename": filename})
        except Exception as e:
            print(f"Error deleting document {filename} from vector store: {e}")

    def query_context(
        self, active_files: list[str], query_text: str, n_results: int = 5
    ) -> list[dict]:
        """
        Queries ChromaDB for relevant text chunks, filtered strictly by active files.
        Returns a list of dictionaries with document, filename, and distance.

        Args:
            active_files: List of filenames to search within.
            query_text: The query string.
            n_results: Maximum number of results to return.

        Returns:
            List of dicts with keys 'document', 'filename', 'distance'.
        """
        if self.collection is None:
            # ChromaDB unavailable; return empty results
            return []

        if not active_files or not query_text.strip():
            return []

        # Enforce strict metadata filtering so we only search files in the active corpus
        if len(active_files) == 1:
            where_filter = {"filename": active_files[0]}
        else:
            where_filter = {"filename": {"$in": active_files}}

        try:
            results = self.collection.query(
                query_texts=[query_text], n_results=n_results, where=where_filter
            )

            # Build structured results
            formatted_results = []
            if results and "documents" in results and results["documents"]:
                for doc, metadata, distance in zip(
                    results["documents"][0],
                    results["metadatas"][0],
                    results["distances"][0],
                ):
                    formatted_results.append(
                        {
                            "document": doc,
                            "filename": metadata.get("filename"),
                            "distance": distance,
                        }
                    )

            return formatted_results

        except Exception as e:
            print(f"Error querying ChromaDB vector space: {e}")
            return []
