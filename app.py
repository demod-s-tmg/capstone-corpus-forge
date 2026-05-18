import os
from flask import Flask
from routes.ingestion import ingestion_bp
from routes.chat import chat_bp  # 1. Import the chat blueprint

app = Flask(__name__)
app.secret_key = "super_secret_key_for_corpus_forge"

# Global Configurations
app.config["UPLOAD_FOLDER"] = "data"
app.config["MAX_FILE_SIZE"] = 10 * 1024 * 1024
app.config["MAX_CONTENT_LENGTH"] = 11 * 1024 * 1024

os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

# Register blueprints
app.register_blueprint(ingestion_bp)
# Register the chat blueprint under the '/chat' prefix to avoid route collisions
app.register_blueprint(chat_bp, url_prefix="/chat")  # 2. Register it with the Flask application

if __name__ == "__main__":
    app.run(debug=True, port=5000)
