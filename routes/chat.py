"""Blueprint reserved for chat and future GenAI workflows."""

from flask import Blueprint, render_template, session


chat_bp = Blueprint("chat", __name__)


@chat_bp.route("/chat")
def chat():
    active_corpus = session.get("active_corpus", [])
    return render_template("chat.html", active_corpus=active_corpus)