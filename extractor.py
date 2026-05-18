"""Helpers for extracting raw text from uploaded files."""

from __future__ import annotations

import os

import pdfplumber


def extract_text_from_txt(file_path: str) -> str:
    with open(file_path, "r", encoding="utf-8", errors="replace") as file_handle:
        return file_handle.read()


def extract_text_from_md(file_path: str) -> str:
    return extract_text_from_txt(file_path)


def extract_text_from_py(file_path: str) -> str:
    return extract_text_from_txt(file_path)


def extract_text_from_js(file_path: str) -> str:
    return extract_text_from_txt(file_path)


def extract_text_from_pdf(file_path: str) -> str:
    extracted_pages = []

    with pdfplumber.open(file_path) as pdf_file:
        for page in pdf_file.pages:
            page_text = page.extract_text() or ""
            if page_text:
                extracted_pages.append(page_text)

    return "\n".join(extracted_pages)


def extract_text_from_file(file_path: str) -> str:
    extension = os.path.splitext(file_path)[1].lower()

    if extension == ".pdf":
        return extract_text_from_pdf(file_path)
    if extension == ".txt":
        return extract_text_from_txt(file_path)
    if extension == ".md":
        return extract_text_from_md(file_path)
    if extension == ".py":
        return extract_text_from_py(file_path)
    if extension == ".js":
        return extract_text_from_js(file_path)

    raise ValueError(f"Unsupported file extension: {extension}")