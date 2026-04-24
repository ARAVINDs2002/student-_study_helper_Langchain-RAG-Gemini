# 🎓 Student AI Assistant — Complete Documentation

> A smart, local AI-powered study tool that answers questions, reads your documents, generates visual flowcharts, and fetches reference images — all from a clean, modern browser UI.

---

## 📌 Table of Contents

1. [Visual Demos](#-visual-demos)
2. [What This App Does](#-what-this-app-does)
3. [Project Structure](#-project-structure)
4. [How It Works — External (User View)](#-how-it-works--external-user-view)
5. [How It Works — Internal (Developer View)](#-how-it-works--internal-developer-view)
6. [File-by-File Breakdown](#-file-by-file-breakdown)
7. [Key Functions Reference](#-key-functions-reference)
8. [Libraries & Dependencies](#-libraries--dependencies)
9. [Data Flow Diagrams](#-data-flow-diagrams)
10. [Backend Status Indicator](#-backend-status-indicator)
11. [Getting Started](#-getting-started)

---

## 📺 Visual Demos

### 🤖 Ask AI Mode
In this mode, the AI provides clear explanations, relevant web images, and a dynamic flowchart if a process is detected.
![Ask AI Mode Demo](https://github.com/ARAVINDs2002/student-_study_helper_Langchain-RAG-Gemini/raw/main/assets/ask_ai.gif)


### 📄 Ask RAG Mode (RAG)
In this mode, you can upload your own study materials (PDF/TXT) and the AI will answer questions based strictly on that content.

![Ask AI Mode Demo](https://github.com/ARAVINDs2002/student-_study_helper_Langchain-RAG-Gemini/raw/main/assets/ask_ai.gif)

## 🧠 What This App Does

The **Student AI Assistant** is a full-stack AI web application with two core modes:

| Mode | Description |
|------|-------------|
| **Ask AI (Gemini Mode)** | Ask any academic question. The AI (Google Gemini) provides structured answers including explanations, conditional flowcharts, and web-fetched reference images. |
| **Chat with Doc (RAG Mode)** | Upload PDF or TXT study notes. The AI reads **only your document** and answers questions based strictly on its content, falling back to general knowledge if needed. |

Every response automatically includes:
- ✅ A **clear explanation** of the topic.
- 📊 **Smart Step-by-Step Workflow**: A visual flowchart (PNG) rendered server-side only when the AI detects a **process or sequence** (e.g., "How it works").
- 🖼️ **Visual reference images** fetched live from Bing Images.

---

## 📁 Project Structure (Cleaned & Production-Ready)

```
student/
│
├── start.bat                  ← One-click launcher (starts backend + opens browser)
│
├── frontend/
│   ├── index.html             ← Main UI page (single page app)
│   ├── style.css              ← All styling (glassmorphism dark theme)
│   └── script.js              ← All frontend logic (API calls, rendering, status polling)
│
├── backend/
│   ├── main.py                ← FastAPI server — defines all API routes
│   ├── llm.py                 ← AI Logic: Smart prompts for conditional flowchart generation
│   ├── rag.py                 ← Document upload, chunking, vector search (RAG pipeline)
│   ├── utils.py               ← Utilities: Image scraping + clean flowchart PNG generation
│   ├── requirements.txt       ← All Python dependencies
│   └── .env                   ← Your secret API key (never share this!)
│
└── venv/                      ← Python virtual environment (auto-created)
```

---

## 👤 How It Works — External (User View)

### Step 1 — Launch
Double-click `start.bat`. Your browser opens `frontend/index.html` automatically once the server initializes.

### Step 2 — Status Check
The sidebar features a live **Backend Status Indicator**. It transitions from **Connecting...** (🟡) to **Online** (🟢) when the server is ready. Chatting is disabled while the backend is offline.

### Step 3 — Smart Interaction
1. Type a question.
2. The AI identifies if the topic describes a **sequence** (e.g., "How is rain made?") or a **definition** (e.g., "What is gravity?").
3. **If it's a sequence**: A numbered, color-coded flowchart is generated and displayed.
4. **If it's a fact/definition**: The flowchart is skipped to keep the UI clean.
5. Thumbnail reference images are always displayed for visual context.

---

## ⚙️ How It Works — Internal (Developer View)

### Smart Flowchart Logic
The AI (Gemini) is instructed via strict system prompts in `llm.py` to evaluate the content before responding. If the answer doesn't contain a logical sequence of steps, the `flowchart` field in the JSON response is returned as an empty array `[]`. The backend and frontend are built to skip rendering when this array is empty.

### Clean Image Rendering
The flowchart PNGs are rendered using `Matplotlib` in `utils.py`. All internal image titles have been removed to avoid redundancy with the frontend UI headers, resulting in a cleaner, professional look.

### LLM JSON Contract
```json
{
  "subject": "Topic name",
  "explanation": "Clear explanation in 2-4 sentences",
  "flowchart": ["Step 1", "Step 2", ...], // Empty [] if no process exists
  "image_query": "search query"
}
```

---

## 📄 File-by-File Breakdown

### `backend/llm.py` — The Decision Maker
- Defines the "Smart Prompting" logic.
- Instructs the AI on when to generate steps vs. when to return an empty list.
- Manages chat history to ensure the AI understands follow-up questions.

### `backend/utils.py` — The Renderer & Scraper
- **Flowchart Engine**: Uses `Matplotlib` with `textwrap` to ensure labels are perfectly centered and never truncated.
- **Image Scraper**: Uses `BeautifulSoup` to find high-quality thumbnails on Bing Images without being blocked.

### `backend/rag.py` — Document Intelligence
- Implements Retrieval-Augmented Generation.
- Uses `all-MiniLM-L6-v2` for local embeddings (no extra cost/API calls).
- Stores data in a `FAISS` vector database for lightning-fast lookups.

---

## 🚀 Getting Started

1. **Setup API Key**: Add your `GOOGLE_API_KEY` to `backend/.env`.
2. **Launch**: Run `start.bat`.
3. **Wait for Online Status**: Once the dot in the sidebar turns 🟢, you are ready to study!

---

## 🛠️ Key Libraries Used
- **FastAPI**: Backend API
- **LangChain**: AI Orchestration
- **Google Gemini**: LLM Brain
- **FAISS**: Vector Search
- **Matplotlib**: Flowchart Rendering
- **BeautifulSoup**: Image Scraping

Happy studying! 🎓
