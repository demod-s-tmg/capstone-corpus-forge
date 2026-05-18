"""Blueprint for corpus ingestion, file management, and active corpus selection."""

from __future__ import annotations

import os

from flask import Blueprint, current_app, flash, redirect, render_template, request, session, url_for
from werkzeug.utils import secure_filename

from utils import allowed_file, validate_file_content
from extractor import extract_text_from_file


ingestion_bp = Blueprint("ingestion", __name__)


@ingestion_bp.route("/")
def index():
    files = os.listdir(current_app.config["UPLOAD_FOLDER"])
    active_corpus = session.get("active_corpus", [])
    active_corpus = [file for file in active_corpus if file in files]
    session["active_corpus"] = active_corpus
    return render_template("index.html", files=files, active_corpus=active_corpus)


@ingestion_bp.route("/active-corpus", methods=["POST"])
def update_active_corpus():
    current_files = set(os.listdir(current_app.config["UPLOAD_FOLDER"]))
    selected_files = request.form.getlist("active_files")

    active_corpus = []
    for filename in selected_files:
        secure_name = secure_filename(filename)
        if secure_name in current_files and secure_name not in active_corpus:
            active_corpus.append(secure_name)

    session["active_corpus"] = active_corpus
    flash("Active corpus updated.")
    return redirect(url_for("ingestion.index"))


@ingestion_bp.route("/upload", methods=["POST"])
def upload_file():
    if "document" not in request.files:
        flash("No file part")
        return redirect(url_for("ingestion.index"))

    file = request.files["document"]
    original_filename = file.filename or ""

    if original_filename == "":
        flash("No selected file")
        return redirect(url_for("ingestion.index"))

    if not allowed_file(original_filename):
        flash("Invalid file type. Please upload .txt, .md, .pdf, .py, or .js files.")
        return redirect(url_for("ingestion.index"))

    is_valid, error_msg = validate_file_content(file, original_filename)
    if not is_valid:
        flash(f"File validation failed: {error_msg}")
        return redirect(url_for("ingestion.index"))

    file.seek(0, os.SEEK_END)
    file_size = file.tell()
    file.seek(0)

    if file_size > current_app.config["MAX_FILE_SIZE"]:
        flash(
            f"File too large. Maximum size is {current_app.config['MAX_FILE_SIZE'] / 1024 / 1024:.1f} MB"
        )
        return redirect(url_for("ingestion.index"))

    if file_size == 0:
        flash("File is empty")
        return redirect(url_for("ingestion.index"))

    filename = secure_filename(original_filename)
    file_path = os.path.join(current_app.config["UPLOAD_FOLDER"], filename)
    file.save(file_path)

    extracted_text = extract_text_from_file(file_path)
    flash(
        f"File {filename} successfully uploaded and extracted ({len(extracted_text)} characters)."
    )
    return redirect(url_for("ingestion.index"))


@ingestion_bp.route("/delete/<filename>", methods=["POST"])
def delete_file(filename):
    secure_name = secure_filename(filename)
    if not secure_name:
        flash("Invalid file name.")
        return redirect(url_for("ingestion.index"))

    upload_root = os.path.abspath(current_app.config["UPLOAD_FOLDER"])
    file_path = os.path.abspath(os.path.join(upload_root, secure_name))

    if os.path.commonpath([upload_root, file_path]) != upload_root:
        flash("Invalid file path.")
        return redirect(url_for("ingestion.index"))

    if os.path.exists(file_path) and os.path.isfile(file_path):
        os.remove(file_path)
        active_corpus = session.get("active_corpus", [])
        if secure_name in active_corpus:
            session["active_corpus"] = [file for file in active_corpus if file != secure_name]
        flash(f"File {secure_name} successfully deleted.")
    else:
        flash(f"Error: File {secure_name} not found.")

    return redirect(url_for("ingestion.index"))