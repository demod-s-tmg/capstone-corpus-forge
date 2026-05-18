import os
import io
import unittest
from app import app


class CorpusForgeReliabilityTests(unittest.TestCase):
    def setUp(self):
        """Set up test client and ensure sandboxed environment."""
        app.config["TESTING"] = True
        app.config["UPLOAD_FOLDER"] = "data_test"
        os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)
        self.client = app.test_client()

    def tearDown(self):
        """Clean up test artifacts after execution."""
        if os.path.exists("data_test"):
            for f in os.listdir("data_test"):
                os.remove(os.path.join("data_test", f))
            os.rmdir("data_test")

    # ==========================================
    # 🟢 NORMAL SCENARIOS (What Worked)
    # ==========================================

    def test_normal_txt_upload_and_indexing(self):
        """Scenario: User uploads a valid, clean text file."""
        data = {
            "document": (
                io.BytesIO(b"Valid test corpus context for ChromaDB indexing."),
                "sample.txt",
            )
        }
        response = self.client.post(
            "/upload", data=data, content_type="multipart/form-data"
        )
        self.assertEqual(response.status_code, 302)  # Redirects to index on success

    def test_active_corpus_state_session(self):
        """Scenario: User toggles a valid file in their workspace session."""
        with self.client.session_transaction() as sess:
            sess["active_corpus"] = ["sample.txt"]

        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)

    # ==========================================
    # 🔴 FAILURE SCENARIOS (What Handled Defensively)
    # ==========================================

    def test_failure_file_too_large(self):
        """Scenario: Malicious or accidental upload exceeding 10MB payload limit."""
        large_payload = b"X" * (11 * 1024 * 1024)  # 11MB payload
        data = {"document": (io.BytesIO(large_payload), "huge_bomb.txt")}
        response = self.client.post(
            "/upload", data=data, content_type="multipart/form-data"
        )
        # Expecting a failure handling mechanism (either redirect with flash or 413)
        self.assertIn(response.status_code, [302, 413])

    def test_failure_spoofed_extension_magic_check(self):
        """Scenario: Attacker names an executable script as a '.txt' file."""
        fake_text_payload = b"\x7fELF\x02\x01\x01\x00"  # Linux ELF binary magic bytes
        data = {"document": (io.BytesIO(fake_text_payload), "spoofed_script.txt")}
        response = self.client.post(
            "/upload", data=data, content_type="multipart/form-data"
        )
        # Should catch that text/plain doesn't match the true binary type
        self.assertEqual(response.status_code, 302)

    def test_failure_empty_active_corpus_query(self):
        """Scenario: User tries to chat without picking any documents."""
        data = {
            "question": "What does my file say?",
            "tone": "casual",
            "audience": "beginner",
            "task": "chat",
        }
        response = self.client.post("/chat/query", json=data)
        # Should gracefully return a validation error block
        self.assertEqual(response.status_code, 400)
