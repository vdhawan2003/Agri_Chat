# 🌾 Sustainable Agriculture Chatbot (RAG-based Project)

This project is a full-stack **Retrieval-Augmented Generation (RAG) Agriculture Chatbot**.  
It answers agriculture-related questions using a **CSV knowledge base** combined with **AI-based text generation**.

The chatbot first retrieves answers from a structured CSV file using **BM25 ranking + fuzzy matching**, and only then uses **Gemini AI** to enhance or format responses.

==================================================

📁 PROJECT STRUCTURE

project-root/
├── backend/
│   ├── api_server.py
│   ├── rag_core.py
│   ├── gemini_api.py
│   └── data/
│       └── agriculture_facts.csv
│
├── frontend/
│   ├── src/
│   │   └── App.js
│   └── package.json
│
├── venv/
└── README.md

==================================================

🧠 HOW THE SYSTEM WORKS (RAG FLOW)

1. User types a question in the React frontend UI.
2. React (App.js) sends a POST request to FastAPI backend.
3. Backend processes the query:
    - Normalizes user text
    - Searches CSV data using BM25
    - Applies fuzzy matching
4. If found, the CSV answer is returned.
5. If formatting is required (points / explanation / translation), Gemini AI is used.
6. The final answer is sent back to frontend and displayed.

This is a true RAG system because retrieval always happens before generation.

==================================================

⚙️ BACKEND SETUP (FASTAPI + VENV)

Step 1: Create virtual environment

python -m venv venv

Step 2: Activate the virtual environment (Windows)

venv\Scripts\activate

Step 3: Install backend dependencies

pip install fastapi uvicorn pandas rank-bm25 rapidfuzz python-dotenv google-generativeai

Step 4: Run backend server

uvicorn backend.api_server:app --reload --port 8001

Backend will run at:
http://127.0.0.1:8001

==================================================

🎨 FRONTEND SETUP (REACT USING App.js + npm start)

Step 1: Go to frontend folder

cd frontend

Step 2: Install dependencies

npm install

Step 3: Start React app

npm start

Frontend will run at:
http://localhost:3000

==================================================

🔗 API CONNECTION

Frontend sends requests to this backend URL:

http://127.0.0.1:8001/chat

__________________________________________________

📄 EXAMPLE API FLOW

Frontend sends:
POST /chat
{
  "query": "What is drip irrigation?"
}

Backend responds:
{
  "response": "Drip irrigation delivers water directly to plant roots..."
}

Frontend displays this response.

==================================================

✅ FEATURES

- CSV-only knowledge base
- BM25 ranking system
- Fuzzy text matching
- Gemini AI integration
- Bullet-point mode
- Explanation mode
- Multi-language responses
- Translation + transliteration

==================================================

📌 PROJECT SUMMARY

This project is a complete **RAG-based Agriculture Chatbot** built with:

Frontend: React (App.js) using npm start  
Backend: FastAPI with Python Virtual Environment  
Database: CSV (No SQL required)  
AI Model: Gemini AI for response refinement
