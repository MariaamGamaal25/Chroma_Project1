import os
from dotenv import load_dotenv
import google.generativeai as genai
from fastapi import APIRouter, HTTPException
from dtos.question_request import QuestionRequest
from dtos.ask_request import AskRequest
from chroma_functionalities import collection

# --- Load environment variables ---
load_dotenv()
API_KEY = os.getenv("GEMINI_API_KEY")
if not API_KEY:
    raise RuntimeError("❌ GEMINI_API_KEY is not set in environment variables")

# --- Configure Gemini API ---
genai.configure(api_key=API_KEY)
MODEL_NAME = "gemini-2.0-flash"
model = genai.GenerativeModel(MODEL_NAME)

router = APIRouter()

# --- Normal Gemini question answering ---
@router.post("/ask-gemini")
async def ask_gemini_endpoint(req: QuestionRequest):
    """
    Sends the question to Gemini and returns an answer (max 500 characters).
    """
    try:
        response = model.generate_content(req.question)
        answer = (response.text or "").strip()

        if len(answer) > 500:
            answer = answer[:500].rstrip() + "..."

        return {
            "question": req.question,
            "answer": answer
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error from Gemini API: {str(e)}")


# --- RAG with ChromaDB ---
@router.post("/ask_rag")
def ask_with_rag(req: AskRequest):
    """
    Retrieve documents from ChromaDB and answer using Gemini.
    """
    try:
        if not hasattr(req, "query"):
            raise HTTPException(status_code=400, detail="Missing 'query' field in request body")

        query_text = req.query  

        # Step 1: Retrieve documents
        retrieved = collection.query(
            query_texts=[query_text],
            n_results=3
        )
        retrieved_docs = retrieved.get("documents", [[]])[0]
        retrieved_metadata = retrieved.get("metadatas", [[]])[0]

        if not retrieved_docs:
            raise HTTPException(status_code=404, detail="No documents found for the query.")

        # Step 2: Build context
        context_text = "\n\n".join([
            f"Source: {retrieved_metadata[i].get('source', 'unknown')}\nContent: {retrieved_docs[i]}"
            for i in range(len(retrieved_docs))
        ])

        # Step 3: Ask Gemini with context
        prompt = (
            f"You are an assistant with access to the following policy documents:\n\n"
            f"{context_text}\n\n"
            f"Answer the following question based only on the above context:\n"
            f"{query_text}"
        )

        response = model.generate_content(prompt)
        answer = response.text.strip()

        # Step 4: Return results
        return {
            "query": query_text,
            "answer": answer,
            "documents_used": [
                {
                    "doc": retrieved_docs[i],
                    "metadata": retrieved_metadata[i]
                }
                for i in range(len(retrieved_docs))
            ]
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"RAG pipeline failed: {str(e)}")
