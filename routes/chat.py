"""Blueprint reserved for chat and future GenAI workflows."""

import os
try:
    from openai import OpenAI
    from openai.error import APIError
except Exception:
    OpenAI = None  # type: ignore
    APIError = Exception  # type: ignore

try:
    import google.generativeai as genai
except Exception:
    genai = None
from flask import Blueprint, jsonify, render_template, request, session

from vector_store import VectorStoreManager


chat_bp = Blueprint("chat", __name__)
v_store = VectorStoreManager()

# Configure the OpenAI client (kept as fallback) and the Gemini client
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if OPENAI_API_KEY and OpenAI is not None:
    try:
        client = OpenAI(api_key=OPENAI_API_KEY)
    except Exception:
        client = None
else:
    client = None

# Configure Google Generative AI (Gemini) client using environment variable
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
genai_client = None
if GEMINI_API_KEY and genai is not None:
    try:
        # prefer configure if available
        if hasattr(genai, "configure"):
            genai.configure(api_key=GEMINI_API_KEY)
            genai_client = genai
        elif hasattr(genai, "Client"):
            genai_client = genai.Client(api_key=GEMINI_API_KEY)
        else:
            genai_client = genai
    except Exception:
        genai_client = None


@chat_bp.route("/")
def chat():
    active_corpus = session.get("active_corpus", [])
    openai_available = bool(OPENAI_API_KEY and client)
    gemini_available = bool(GEMINI_API_KEY and genai_client)
    return render_template(
        "chat.html",
        active_corpus=active_corpus,
        openai_available=openai_available,
        gemini_available=gemini_available,
    )


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

    # Require at least one configured model (Gemini or OpenAI)
    if not ((GEMINI_API_KEY and genai_client) or (OPENAI_API_KEY and client)):
        return (
            jsonify({"error": "No generative AI API key configured (GEMINI_API_KEY or OPENAI_API_KEY)."}),
            500,
        )

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

    # Prefer Gemini (Google Generative AI) if available
    full_prompt = f"{system_prompt}\n\n{user_prompt}"

    try:
        ai_response_text = None

        if GEMINI_API_KEY and genai_client:
            # Try several possible SDK call patterns to support different genai versions
            try:
                # Pattern 1: genai.generate_text
                if hasattr(genai_client, "generate_text"):
                    model_name = os.environ.get("GEMINI_MODEL", "text-bison-001")
                    resp = genai_client.generate_text(model=model_name, prompt=full_prompt)
                    ai_response_text = getattr(resp, "text", None) or (
                        resp.candidates[0].text if getattr(resp, "candidates", None) else None
                    )

                # Pattern 2: genai.chat.create (chat API)
                elif hasattr(genai_client, "chat") and hasattr(genai_client.chat, "create"):
                    model_name = os.environ.get("GEMINI_MODEL", "chat-bison-001")
                    resp = genai_client.chat.create(
                        model=model_name,
                        messages=[{"role": "system", "content": system_prompt}, {"role": "user", "content": user_prompt}],
                    )
                    # try common response shapes
                    ai_response_text = getattr(resp, "output", None)
                    if isinstance(ai_response_text, list) and ai_response_text:
                        # join pieces
                        ai_response_text = "\n".join(
                            [getattr(item, "content", item) for item in ai_response_text]
                        )
                    else:
                        ai_response_text = getattr(resp, "content", None) or ai_response_text

                # Pattern 3: genai.generate
                elif hasattr(genai_client, "generate"):
                    resp = genai_client.generate(input=full_prompt)
                    ai_response_text = getattr(resp, "output_text", None) or (
                        resp.candidates[0].text if getattr(resp, "candidates", None) else None
                    )

            except Exception as gen_err:
                # If Gemini call fails, raise to be handled below and possibly fallback
                gen_err_msg = f"Gemini generation error: {gen_err}"
                raise RuntimeError(gen_err_msg)

        # If Gemini didn't produce output, fall back to OpenAI if available
        if not ai_response_text and OPENAI_API_KEY and client:
            try:
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

                ai_response_text = response.choices[0].message.content if response.choices else None
            except Exception as oe:
                raise RuntimeError(f"OpenAI generation error: {oe}")

        if not ai_response_text:
            ai_response_text = "No response generated."

        return jsonify(
            {
                "response": ai_response_text,
                "context_sources": [chunk["filename"] for chunk in context_chunks],
                "chunks_retrieved": len(context_chunks),
            }
        )

    except Exception as e:
        return jsonify({"error": f"Error generating response: {str(e)}"}), 500