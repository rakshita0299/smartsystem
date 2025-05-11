#  Smart Multi-Agent Q&A System

This project is a lightweight web-based assistant that can answer user questions by smartly choosing between different tools. It combines OpenAI's language models with custom logic to decide how to best answer a query—whether by calculating, looking up a definition, or pulling information from documents you've provided.

---

##  What It Can Do

This assistant knows how to pick the right tool for the job:

- **Calculator**: Handles math queries like "calculate 12 * 9"
-  **Dictionary**: Looks up definitions for words like "define entropy"
-  **RAG (Retrieval-Augmented Generation)**: Answers general questions by searching through your uploaded documents

It uses:
- **LangChain** for connecting tools and LLMs
- **OpenAI GPT** for language understanding
- **FAISS** for fast, vector-based document search
- **Flask** + **HTML/JS** for a clean interface

---

## Folder Structure
├── app.py # Main backend logic (Flask server + agent routing)
├── index.html # Simple front-end UI
├── docs/ # Folder for your reference documents (txt files)
├── .env # Environment file containing your API key


---

## 💡 How It Works

1. You add text files to the `docs/` folder
2. The app reads and splits them into chunks for better searching
3. It builds a searchable vector index using FAISS
4. When a user submits a question:
   - If it's math-related → uses a built-in calculator
   - If it looks like a definition → queries an open dictionary API
   - Otherwise → retrieves related content and asks the LLM to answer

---

## 🧪 Example Queries

You can try questions like:

- `"Calculate 13 + (4 * 3)"`
- `"Define photosynthesis"`
- `"What are the key features of the new product?"`

---

## ⚙️ Setup Instructions

### 1. Install dependencies

First, make sure Python is installed, then run:

pip install -r requirements.txt

2. Add your documents
Place any .txt or .md files in the docs/ directory.

3. Create a .env file
This file should be in your project root and contain your OpenAI key:
OPENAI_API_KEY=your_openai_api_key_here

4. Run the app
Start the server using:
python app.py
Then visit http://localhost:5000 in your browser.
