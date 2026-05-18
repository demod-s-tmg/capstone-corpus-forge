import magic

ALLOWED_EXTENSIONS = {"txt", "md", "pdf", "py", "js"}

ALLOWED_MIMES = {
    "text/plain": {"txt"},
    "text/markdown": {"md"},
    "application/pdf": {"pdf"},
    "text/x-python": {"py"},
    "application/javascript": {"js"},
    "text/javascript": {"js"},
}


def allowed_file(filename: str) -> bool:
    """Check if filename has allowed extension."""
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def validate_file_content(file_obj, filename: str) -> tuple[bool, str | None]:
    """Validate file content using magic numbers."""
    file_obj.seek(0)
    file_bytes = file_obj.read(512)
    file_obj.seek(0)

    try:
        mime = magic.from_buffer(file_bytes, mime=True)
    except Exception:
        return False, "Could not determine file type"

    if "." not in filename:
        return False, "Invalid filename"

    ext = filename.rsplit(".", 1)[1].lower()

    if mime not in ALLOWED_MIMES:
        return False, f"File type {mime} not allowed"

    if ext not in ALLOWED_MIMES[mime]:
        return False, f"Extension .{ext} does not match actual file type {mime}"

    return True, None
