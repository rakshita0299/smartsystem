from flask import Flask, render_template, request, jsonify
from langchain_community.embeddings import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.chat_models import ChatOpenAI
from langchain.schema import Document
from dotenv import load_dotenv
import os
import requests
import logging

# Setup logging and load environment variables
logging.basicConfig(level=logging.INFO)
load_dotenv()

api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise ValueError("OPENAI_API_KEY is missing in your .env file")

app = Flask(__name__)

# Load and chunk documents from the 'docs' folder
def load_documents():
    docs = []
    if not os.path.exists("docs"):
        os.makedirs("docs")
        logging.warning("Created 'docs' directory.")

    for filename in os.listdir("docs"):
        with open(f"docs/{filename}", "r") as f:
            docs.append(Document(page_content=f.read()))
    return docs

def chunk_documents(documents):
    splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    return splitter.split_documents(documents)

# Create a vector store using FAISS
class Retriever:
    def __init__(self, chunks):
        embeddings = OpenAIEmbeddings(openai_api_key=api_key)
        self.index = FAISS.from_documents(chunks, embeddings)

    def get_relevant_chunks(self, query, k=3):
        return self.index.similarity_search(query, k=k)

# Initialize the LLM
class AnswerGenerator:
    def __init__(self):
        self.llm = ChatOpenAI(temperature=0, openai_api_key=api_key)

    def generate(self, context, question):
        prompt = f"Context: {context}\nQuestion: {question}\nAnswer:"
        return self.llm.predict(prompt)

# Handle different query types: math, dictionary, general
class QueryHandler:
    def __init__(self, retriever, generator):
        self.retriever = retriever
        self.generator = generator

    def handle(self, query):
        query_lower = query.lower()

        if any(keyword in query_lower for keyword in ["calculate", "compute", "math"]):
            return self._handle_calculation(query)

        elif any(keyword in query_lower for keyword in ["define", "meaning", "what is"]):
            return self._handle_definition(query)

        else:
            return self._handle_rag(query)

    def _handle_calculation(self, query):
        logging.info("Using Calculator")
        try:
            expression = ''.join(c for c in query if c.isdigit() or c in '+-*/(). ')
            result = str(eval(expression))
        except:
            result = "Invalid calculation"
        return {"tool_used": "Calculator", "result": result, "context": None}

    def _handle_definition(self, query):
        logging.info("Using Dictionary")
        word = query.split()[-1]
        try:
            response = requests.get(f"https://api.dictionaryapi.dev/api/v2/entries/en/{word}")
            if response.ok:
                definition = response.json()[0]['meanings'][0]['definitions'][0]['definition']
                return {"tool_used": "Dictionary", "result": definition, "context": None}
            else:
                return {"tool_used": "Dictionary", "result": "Definition not found", "context": None}
        except:
            return {"tool_used": "Dictionary", "result": "Error fetching definition", "context": None}

    def _handle_rag(self, query):
        logging.info("Using RAG")
        chunks = self.retriever.get_relevant_chunks(query)
        context = "\n".join([chunk.page_content for chunk in chunks])
        answer = self.generator.generate(context, query)
        return {"tool_used": "RAG", "result": answer, "context": context}

# Initialize everything
documents = load_documents()
chunks = chunk_documents(documents)
retriever = Retriever(chunks)
generator = AnswerGenerator()
handler = QueryHandler(retriever, generator)

# Web routes
@app.route('/')
def home():
    return render_template('index.html')

@app.route('/query', methods=['POST'])
def query():
    try:
        query = request.json['query']
        result = handler.handle(query)
        return jsonify(result)
    except Exception as e:
        logging.error(f"Query error: {str(e)}")
        return jsonify({
            "tool_used": "Error",
            "result": f"An error occurred: {str(e)}",
            "context": None
        }), 500

if __name__ == '__main__':
    app.run(debug=True)
