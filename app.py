import os
import magic
from flask import Flask, render_template, request, redirect, url_for, flash
from werkzeug.utils import secure_filename

from extractor import extract_text_from_file

# MIME type mappings for validation (magic numbers)
ALLOWED_MIMES = {
    "text/plain": {"txt"},
    "text/markdown": {"md"},
    "application/pdf": {"pdf"},
    "text/x-python": {"py"},
    "application/javascript": {"js"},
    "text/javascript": {"js"},
}

app = Flask(__name__)
app.secret_key = "super_secret_key_for_corpus_forge"  # Needed for flashing messages

# Configuration for file uploads
UPLOAD_FOLDER = "data"
ALLOWED_EXTENSIONS = {"txt", "md", "pdf", "py", "js"}  # Required file types
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB limit

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["MAX_CONTENT_LENGTH"] = MAX_FILE_SIZE  # Flask request size limit

# Ensure the upload folder exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


def allowed_file(filename):
    """Check if filename has allowed extension."""
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def validate_file_content(file_obj, filename):
    """
    Validate file content using magic numbers (file signatures).
    Returns (is_valid, error_message).
    """
    # Read first few bytes to check magic number
    file_obj.seek(0)
    file_bytes = file_obj.read(512)  # Read first 512 bytes
    file_obj.seek(0)  # Reset file pointer for saving
    
    # Get actual MIME type from file content (magic numbers)
    try:
        mime = magic.from_buffer(file_bytes, mime=True)
    except Exception:
        return False, "Could not determine file type"
    
    # Get file extension
    if "." not in filename:
        return False, "Invalid filename"
    
    ext = filename.rsplit(".", 1)[1].lower()
    
    # Check if MIME type matches claimed extension
    if mime not in ALLOWED_MIMES:
        return False, f"File type {mime} not allowed"
    
    if ext not in ALLOWED_MIMES[mime]:
        return False, f"Extension .{ext} does not match actual file type {mime}"
    
    return True, None


@app.route("/")
def index():
    # List files currently in the corpus
    files = os.listdir(app.config["UPLOAD_FOLDER"])
    return render_template("index.html", files=files)


@app.route("/upload", methods=["POST"])
def upload_file():
    if "document" not in request.files:
        flash("No file part")
        return redirect(request.url)

    file = request.files["document"]
    original_filename = file.filename or ""

    if original_filename == "":
        flash("No selected file")
        return redirect(url_for("index"))

    # Step 1: Check extension
    if not allowed_file(original_filename):
        flash("Invalid file type. Please upload .txt, .md, .pdf, .py, or .js files.")
        return redirect(url_for("index"))
    
    # Step 2: Validate file content (magic numbers)
    is_valid, error_msg = validate_file_content(file, original_filename)
    if not is_valid:
        flash(f"File validation failed: {error_msg}")
        return redirect(url_for("index"))
    
    # Step 3: Check file size before saving
    file.seek(0, os.SEEK_END)
    file_size = file.tell()
    file.seek(0)
    
    if file_size > MAX_FILE_SIZE:
        flash(f"File too large. Maximum size is {MAX_FILE_SIZE / 1024 / 1024:.1f} MB")
        return redirect(url_for("index"))
    
    if file_size == 0:
        flash("File is empty")
        return redirect(url_for("index"))
    
    # Step 4: Save file with validation
    filename = secure_filename(original_filename)
    file_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
    file.save(file_path)

    # Step 5: Extract text immediately after saving
    extracted_text = extract_text_from_file(file_path)

    # At this point you can persist, index, or analyze `extracted_text`.
    flash(f"File {filename} successfully uploaded and extracted ({len(extracted_text)} characters).")
    return redirect(url_for("index"))


if __name__ == "__main__":
    app.run(debug=True, port=5000)
