### 15-05-2026 12:47
- **Prompt**: Read the agent folder and activate all the agents and instructions

### 15-05-2026 12:50
- **Prompt**: help me commit once saying first commit on the cloned repo

### 18-05-2026 14:09
- **Prompt**: Test prompt to verify hook is working

### 18-05-2026 14:11
- **Prompt**: Review the upload_file() function in my Flask app. Are there any security vulnerabilities with how I am validating and saving the uploaded files? Specifically, how can I prevent a user from uploading a malicious file disguised with a .pdf extension, and how can I limit the maximum upload file size?

### 18-05-2026 14:19
- **Prompt**: My Flask application currently saves .pdf, .txt, .md, and .py files into a data folder. Write a new Python module called extractor.py. In it, create functions that take a file path as input and return the raw string text of the file. Use pdfplumber for the PDFs. How should I integrate this extraction step into my existing upload_file() route so it processes the text immediately after saving?

### 18-05-2026 14:27
- **Prompt**: Review my index.html and app.py. I need to add a feature to allow users to delete files from the data folder. Please generate the Flask route (/delete/<filename>) to handle secure deletion, and update the HTML template to include a 'Delete' button next to each file in the list

### 18-05-2026 14:29
- **Prompt**: Users also need to select which specific documents are active for their AI chat session. Suggest a UI approach (like checkboxes or a toggle switch in the HTML form) and the corresponding Flask backend logic to keep track of the user's 'active corpus' in their session state

### 18-05-2026 14:38
- **Prompt**: This application is about to grow. We need to add a vector database (ChromaDB) and Generative AI workflows. To keep the code clean and prevent merge conflicts within my team, how can I use Flask Blueprints to split my app.py into separate routing files (e.g., routes/ingestion.py, routes/chat.py)?

### 18-05-2026 14:36
- **Prompt**: Can u add the plans we discussed in the docs folder properly?

