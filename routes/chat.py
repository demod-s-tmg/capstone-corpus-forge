"""Blueprint reserved for chat and future GenAI workflows."""

import os

from openai import OpenAI, APIError
from flask import Blueprint, jsonify, render_template, request, session

from vector_store import VectorStoreManager


chat_bp = Blueprint("chat", __name__)
v_store = VectorStoreManager()

# Configure the OpenAI client
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if OPENAI_API_KEY:
    client = OpenAI(api_key=OPENAI_API_KEY)
else:
    client = None


@chat_bp.route("")
def chat():
    active_corpus = session.get("active_corpus", [])
    return render_template("chat.html", active_corpus=active_corpus)


@chat_bp.route("/query", methods=["POST"])
def query():
    """Handle user queries with grounded context from the active corpus."""
    # Get form parameters
    user_question = request.form.get("question", "").strip()
    tone = request.form.get("tone", "professional").strip()
    audience = request.form.get("audience", "general").strip()
    task = request.form.get("task", "explain").strip()

    # Validate input
    if not user_question:
        return jsonify({"error": "Question cannot be empty."}), 400

    if not OPENAI_API_KEY or not client:
        return jsonify({"error": "OpenAI API key not configured."}), 500

    # Get active corpus from session
    active_corpus = session.get("active_corpus", [])
    if not active_corpus:
        return jsonify({"error": "No documents selected. Please select files to query."}), 400

    # Retrieve context chunks from the vector store
    context_chunks = v_store.query_context(
        active_files=active_corpus, query_text=user_question, n_results=5
    )

    if not context_chunks:
        context_text = "(No relevant context found in the selected documents.)"
    else:
        context_text = "\n\n".join(
            [f"[{chunk['filename']}]\n{chunk['document']}" for chunk in context_chunks]
        )

    # Build the grounded prompt
    system_prompt = f"""You are a helpful assistant with access to document context.
- Tone: {tone}
- Audience: {audience}
- Task: {task}

Provide clear, accurate answers based on the provided context. If the context doesn't contain the answer, acknowledge that and offer what you can."""

    user_prompt = f"""Context from documents:
{context_text}

User question: {user_question}

Please answer the question based on the context above."""

    try:
        # Call the OpenAI API
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0.7,
            max_tokens=1024,
            top_p=0.9,
        )

        ai_response = response.choices[0].message.content if response.choices else "No response generated."

        return jsonify(
            {
                "response": ai_response,
                "context_sources": [chunk["filename"] for chunk in context_chunks],
                "chunks_retrieved": len(context_chunks),
            }
        )

    except APIError as e:
        return jsonify({"error": f"OpenAI API error: {str(e)}"}), 500
    except Exception as e:
        return jsonify({"error": f"Error generating response: {str(e)}"}), 500