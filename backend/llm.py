import os
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate

# =========================
# LLM INIT
# =========================
llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash")

# =========================
# MEMORY STORAGE
# =========================
# Format: {"session_id": ["User: ...", "AI: ..."]}
chat_history_store = {}

def get_history_text(session_id: str) -> str:
    if session_id not in chat_history_store:
        chat_history_store[session_id] = []
    return "\n".join(chat_history_store[session_id])

def add_to_history(session_id: str, question: str, explanation: str):
    if session_id not in chat_history_store:
        chat_history_store[session_id] = []
    chat_history_store[session_id].append(f"User: {question}")
    chat_history_store[session_id].append(f"AI: {explanation}")

# =========================
# BASE CHAIN
# =========================
base_prompt = ChatPromptTemplate.from_template("""
You are a smart student helper. Answer clearly and thoroughly.

Chat History:
{history}

Return ONLY valid JSON — no extra text, no markdown fences.

{{
  "subject": "Topic name",
  "explanation": "Clear, complete explanation in 2-4 sentences",
  "flowchart": ["Step 1", "Step 2", "Step 3"],
  "image_query": "specific google image search query for this topic"
}}

FLOWCHART RULES — follow strictly:
- If the question is about a PROCESS, SEQUENCE, HOW something works, or has clear steps → return an array of 3-8 step strings.
- If the question is a simple DEFINITION ("what is X"), a FACT ("who invented X", "when did X happen"), or has NO logical sequence → return an empty array: []
- NEVER return a flowchart for pure definition or trivia questions.

Question: {question}
""")
base_chain = base_prompt | llm

# =========================
# RAG CHAIN
# =========================
rag_prompt = ChatPromptTemplate.from_template("""
You are a student helper. Answer only from the provided context.

Chat History:
{history}

Context:
{context}

Return ONLY valid JSON — no extra text, no markdown fences.

{{
  "subject": "Topic name",
  "explanation": "Answer ONLY from context in 2-4 sentences. If not found, say 'Not found in document'",
  "flowchart": ["Step 1", "Step 2", "Step 3"],
  "image_query": "specific google image search query for this topic"
}}

FLOWCHART RULES — follow strictly:
- If the answer describes a PROCESS, SEQUENCE, or HOW something works → return an array of 3-8 step strings.
- If the answer is a simple DEFINITION, FACT, or has NO logical sequence → return an empty array: []

Question: {question}
""")
rag_chain = rag_prompt | llm

def invoke_gemini(session_id: str, question: str):
    history_text = get_history_text(session_id)
    return base_chain.invoke({
        "question": question,
        "history": history_text
    })

def invoke_rag(session_id: str, question: str, context: str):
    history_text = get_history_text(session_id)
    return rag_chain.invoke({
        "context": context,
        "question": question,
        "history": history_text
    })
