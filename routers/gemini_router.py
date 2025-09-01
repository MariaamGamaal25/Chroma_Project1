# # routers/gemini_router.py
# import os
# from fastapi import APIRouter, HTTPException
# from dotenv import load_dotenv
# import google.generativeai as genai

# from dtos.question_request import QuestionRequest
# from dtos.ask_request import AskRequest
# from chroma_functionalities import get_chroma_collection

# # --- Load env ---
# load_dotenv()
# API_KEY = os.getenv("GEMINI_API_KEY")
# if not API_KEY:
#     raise RuntimeError("GEMINI_API_KEY is not set in environment variables")

# # --- Configure Gemini ---
# genai.configure(api_key=API_KEY)
# MODEL_NAME = "gemini-2.0-flash"
# model = genai.GenerativeModel(MODEL_NAME)

# router = APIRouter()


# @router.post("/ask-gemini", tags=["Gemini"])
# async def ask_gemini_endpoint(req: QuestionRequest):
#     """
#     Sends a plain question directly to Gemini (no RAG).
#     """
#     try:
#         response = model.generate_content(req.question)
#         answer = (response.text or "").strip()

#         # Safety: avoid super long answers in UI
#         if len(answer) > 500:
#             answer = answer[:500].rstrip() + "..."

#         return {
#             "question": req.question,
#             "answer": answer
#         }
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"Error from Gemini API: {str(e)}")




# @router.post("/ask-rag", tags=["RAG"])
# def ask_with_rag(req: AskRequest):
#     """
#     Retrieve relevant chunks from ChromaDB and answer using Gemini.
#     Answer is structured: direct (✅/❌) + bullet points.
#     """
#     try:
#         if not hasattr(req, "query"):
#             raise HTTPException(status_code=400, detail="Missing 'query' field in request body")

#         query_text = req.query
#         collection = get_chroma_collection()

#         # Retrieve top 3 relevant chunks
#         retrieved = collection.query(
#             query_texts=[query_text],
#             n_results=7
#         )

#         docs = retrieved.get("documents", [[]])[0]
#         metas = retrieved.get("metadatas", [[]])[0]

#         if not docs:
#             raise HTTPException(status_code=404, detail="No documents found for the query.")

#         # Build context with provenance (source + section)
#         context_parts = []
#         for i in range(len(docs)):
#             src = metas[i].get("source", metas[i].get("filename", "unknown"))
#             sec = metas[i].get("section", "")
#             context_parts.append(f"[{src} | {sec}]\n{docs[i]}")

#         context_text = "\n\n".join(context_parts)

#         # --- NEW Structured Prompt ---
# #         prompt = (
# #         f"أنت مساعد ذكي تجيب فقط بالاعتماد على المستندات التالية:\n\n"
# #         f"{context_text}\n\n"
# #         f"--- السؤال ---\n{query_text}\n\n"
# #         f"--- التعليمات ---\n"
# #         f"1. إذا كان السؤال من نوع نعم/لا (مثل: 'هل يشمل كذا؟')، ابدأ بـ ✅ نعم أو ❌ لا، ثم أضف نقاط توضيحية مختصرة.\n"
# #         f"2. إذا كان السؤال وصفي (مثل: 'ما هو كذا؟' أو 'كيف يعمل؟)، أجب مباشرة في شكل نقاط واضحة بدون ✅/❌.\n"
# #         f"3. اجعل الإجابة مختصرة، منظمة، ومعتمدة فقط على المستندات.\n"
# #         f"4. إذا لم تتوفر الإجابة في المستندات، أجب فقط بعبارة: 'غير متوفر في المستند'.\n\n"
# #         f"--- الإجابة النهائية ---"
# # )
#         prompt = (
#         f"You are a helpful assistant that answers **only based on the following documents**:\n\n"
#         f"{context_text}\n\n"
#         f"--- QUESTION ---\n{query_text}\n\n"
#         f"--- INSTRUCTIONS ---\n"
#         f"1. Always answer in **English only**, even if the question is in another language.\n"
#         f"2. If the question is YES/NO type (e.g., 'Does it cover X?'), start with ✅ Yes or ❌ No, then add bullet points with details.\n"
#         f"3. If the question is descriptive (e.g., 'What is X?' or 'How does it work?'), answer directly in clear bullet points without ✅/❌.\n"
#         f"4. Keep answers concise, structured, and based ONLY on the documents.\n"
#         f"5. If the answer is not available in the documents, reply ONLY with: 'Not available in the document'.\n\n"
#         f"--- FINAL ANSWER ---"
#         )

#         response = model.generate_content(prompt)
#         answer = response.text.strip()

#         return {
#             "query": query_text,
#             "answer": answer,
#             "sources": [
#                 {"text": docs[i], "metadata": metas[i]}
#                 for i in range(len(docs))
#             ]
#         }

#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"RAG pipeline failed: {str(e)}")

# import os
# from fastapi import APIRouter, Query
# from chroma_functionalities import get_chroma_collection
# from gemini_client import ask_gemini  # you already had this client wrapper

# router = APIRouter()

# @router.get("/compare")
# async def compare_service(service: str = Query(..., description="Service name to compare")):
#     """
#     Compare Medright 2024 vs Seha One 2025 for a given service.
#     """

#     collection = get_chroma_collection("benefits")

#     results = collection.query(
#         query_texts=[service],
#         n_results=6,
#         where={"service": service}  # metadata filter
#     )

#     docs = results.get("documents", [[]])[0]
#     if not docs:
#         return {"status": "not found", "service": service}

#     # Build comparison prompt
#     joined_context = "\n".join(docs)
#     prompt = f"""
# You are a benefits analyst. Compare Medright 2024 vs Seha One 2025 for the service: {service}.
# Use the following extracted table context:
# ---
# {joined_context}
# ---
# Output a clear English summary of the differences, highlighting limits, coverage rules, and frequency.
# """

#     answer = ask_gemini(prompt)

#     return {
#         "service": service,
#         "context": docs,
#         "answer": answer
#     }


# @router.get("/ping")
# async def ping():
#     return {"status": "gemini router alive"}

# routers/gemini_router.py
import os
from typing import List, Dict, Any

from fastapi import APIRouter, HTTPException
from dotenv import load_dotenv

import google.generativeai as genai

from dtos.question_request import QuestionRequest
from dtos.ask_request import AskRequest
from chroma_functionalities import get_chroma_collection
from utils.enums import Endpoints, Messages

# --- Load env (lazily configure client later) ---
load_dotenv()

router = APIRouter(prefix=Endpoints.API_PREFIX.value, tags=["Gemini"])

# --------- Gemini client (lazy singleton) ---------
_MODEL_NAME = "gemini-2.0-flash"
_genai_configured = False
_model = None

def _ensure_gemini() -> None:
    """Configure the Gemini client once, only when needed."""
    global _genai_configured, _model
    if _genai_configured and _model is not None:
        return
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise HTTPException(status_code=500, detail="GEMINI_API_KEY environment variable is not set.")
    genai.configure(api_key=api_key)
    _model = genai.GenerativeModel(_MODEL_NAME)
    _genai_configured = True


# --------- Prompt builder helpers ---------
def _format_retrieved_pairs(docs: List[str], metas: List[Dict[str, Any]]) -> str:
    """
    Build a compact, model-friendly context from retrieved documents + metadatas.
    Tries to surface structured pairs: service | medright_2024 | seha_one_2025
    """
    lines: List[str] = []
    for text, meta in zip(docs, metas):
        service = (meta or {}).get("service") or ""
        med = (meta or {}).get("medright_2024") or ""
        seha = (meta or {}).get("seha_one_2025") or ""
        page = (meta or {}).get("page")
        src = (meta or {}).get("source") or (meta or {}).get("filename") or "unknown"
        doc_type = (meta or {}).get("doc_type") or "chunk"

        # Prefer structured triple if both med & seha exist; else fall back to free text
        if med or seha or service:
            line = f"[{doc_type}] Service: {service or '—'} | Medright 2024: {med or '—'} | Seha One 2025: {seha or '—'}"
        else:
            # free text fallback
            line = f"[{doc_type}] {text}"

        # provenance hint
        prov = f" (src: {src}"
        if page:
            prov += f", page {page}"
        prov += ")"

        lines.append(line + prov)
    return "\n".join(lines)


def _build_comparison_prompt(service_name: str, service_docs: List[Dict], row_docs: List[Dict]) -> str:
    """
    Compose a strict, English, comparison-oriented prompt.
    service_docs and row_docs are lists of dicts with keys: text, metadata
    """
    s_docs = [d["text"] for d in service_docs]
    s_metas = [d["metadata"] for d in service_docs]
    r_docs = [d["text"] for d in row_docs]
    r_metas = [d["metadata"] for d in row_docs]

    service_block = _format_retrieved_pairs(s_docs, s_metas) if service_docs else "—"
    row_block = _format_retrieved_pairs(r_docs, r_metas) if row_docs else "—"

    prompt = f"""
You are an insurance benefits analyst. Answer **only** using the provided context.
Produce a clear **English** comparison between **Medright 2024** and **Seha One 2025** for the service:
**{service_name}**.

### Strict Output Requirements
1) Start with a one-line verdict that highlights the key difference (or parity) in plain English.
2) Then output a concise **2-column Markdown table** with rows for the most relevant attributes (limits, coverage %, frequency, eligibility, exclusions, notes).
   - Column headers must be exactly: `Attribute | Medright 2024 | Seha One 2025`
   - If an attribute is not stated in context, write `Not stated`.
3) Below the table, add a short bulleted list "Notes" (2–5 bullets max) with any critical conditions or exceptions.
4) Do **not** invent information. If something is not in context, say `Not stated`.

### Service-Level Context (grouped summaries)
{service_block}

### Row-Level Context (granular details)
{row_block}

Now produce the comparison.
""".strip()
    return prompt


def _clip_answer(ans: str, limit: int = 2000) -> str:
    """Safety: prevent extremely long outputs in UI."""
    ans = (ans or "").strip()
    if len(ans) > limit:
        return ans[:limit].rstrip() + "..."
    return ans


# --------- Endpoints ---------
@router.post(Endpoints.ASK_GEMINI.value)
async def ask_gemini_endpoint(req: QuestionRequest):
    """
    Sends a plain question directly to Gemini (no RAG).
    """
    try:
        _ensure_gemini()
        response = _model.generate_content(req.question)
        answer = _clip_answer(getattr(response, "text", "") or "")
        return {"question": req.question, "answer": answer}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error from Gemini API: {str(e)}")


# @router.post(Endpoints.ASK_RAG.value)
# def ask_with_rag(req: AskRequest):
#     """
#     Retrieve relevant 'service' then 'row' docs from Chroma and answer using Gemini.
#     Output is a strict English comparison per the prompt.
#     """
#     try:
#         if not hasattr(req, "query") or not (req.query or "").strip():
#             raise HTTPException(status_code=400, detail="Missing 'query' field in request body.")

#         service_name = req.query.strip()
#         collection = get_chroma_collection()

#         # Retrieve service summaries first (higher priority)
#         service_res = collection.query(
#             query_texts=[service_name],
#             n_results=6,
#             where={"doc_type": "service"}
#         )
#         s_docs = service_res.get("documents", [[]])[0]
#         s_metas = service_res.get("metadatas", [[]])[0] if s_docs else []

#         # Retrieve granular rows for the same service
#         row_res = collection.query(
#             query_texts=[service_name],
#             n_results=10,
#             where={"doc_type": "row", "service": service_name}
#         )
#         r_docs = row_res.get("documents", [[]])[0]
#         r_metas = row_res.get("metadatas", [[]])[0] if r_docs else []

#         if not s_docs and not r_docs:
#             raise HTTPException(status_code=404, detail="No relevant documents found for the query.")

#         # Build comparison prompt
#         service_docs = [{"text": t, "metadata": m} for t, m in zip(s_docs, s_metas)]
#         row_docs = [{"text": t, "metadata": m} for t, m in zip(r_docs, r_metas)]
#         prompt = _build_comparison_prompt(service_name, service_docs, row_docs)

#         # Ask Gemini
#         _ensure_gemini()
#         response = _model.generate_content(prompt)
#         answer = _clip_answer(getattr(response, "text", "") or "")

#         return {
#             "query": service_name,
#             "answer": answer,
#             "sources": {
#                 "service_docs": service_docs,
#                 "row_docs": row_docs
#             }
#         }

#     except HTTPException:
#         raise
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"RAG pipeline failed: {str(e)}")


# @router.post(Endpoints.ASK_RAG.value)
# async def ask_rag(input: AskRequest):
#     try:
#         user_query = input.query.strip()
#         if not user_query:
#             raise HTTPException(status_code=400, detail="Query text missing")

#         collection = get_chroma_collection()

#         results = collection.query(
#             query_texts=[user_query],
#             n_results=10,
#             include=["documents", "metadatas"]
#         )

#         docs = results.get("documents", [[]])[0]
#         metas = results.get("metadatas", [[]])[0]

#         if not docs:
#             return {"answer": "No relevant information found in the knowledge base."}

#         # Build comparison context
#         context_blocks = []
#         for meta in metas:
#             service = meta.get("service", "").strip()
#             med = meta.get("medright_2024", "").strip()
#             seha = meta.get("seha_one_2025", "").strip()
#             if service or med or seha:
#                 context_blocks.append(
#                     f"Service: {service} | Medright 2024: {med} | Seha One 2025: {seha}"
#                 )

#         context = "\n".join(context_blocks)

#         prompt = f"""
# You are comparing two health insurance plans: Medright 2024 vs Seha One 2025.

# User question: {user_query}

# Here are retrieved plan details:
# {context}

# Answer in **English** and structured as a comparison with three sections:
# 1. Medright 2024 coverage
# 2. Seha One 2025 coverage
# 3. Key differences and which one is better
# """

#         # ---- Call Gemini or return the prompt for now ----
#         # Replace this with real Gemini API call
#         # response = genai.generate_text(model="gemini-pro", prompt=prompt)

#         return {
#             "question": user_query,
#             "context_used": context,
#             "answer": prompt  # change to response.text when Gemini integrated
#         }

#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"RAG pipeline failed: {e}")

# import os
# from fastapi import APIRouter, HTTPException
# from dtos.ask_request import AskRequest
# from chroma_functionalities import get_chroma_collection
# from utils.enums import Endpoints

# from google import genai

# # Configure the GenAI client
# client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
# MODEL_NAME = "gemini-2.5-pro"

# router = APIRouter(prefix=Endpoints.API_PREFIX.value, tags=["RAG"])

# @router.post(Endpoints.ASK_RAG.value)
# async def ask_rag(input: AskRequest):
#     user_query = input.query.strip()
#     if not user_query:
#         raise HTTPException(status_code=400, detail="Query text missing")

#     collection = get_chroma_collection()
#     results = collection.query(
#         query_texts=[user_query],
#         n_results=10,
#         include=["documents", "metadatas"]
#     )
#     docs = results.get("documents", [[]])[0]
#     metas = results.get("metadatas", [[]])[0]

#     if not docs:
#         return {"answer": "No relevant information found in the knowledge base."}

#     context = "\n".join(
#         f"Service: {meta.get('service','')} | Medright 2024: {meta.get('medright_2024','')} | Seha One 2025: {meta.get('seha_one_2025','')}"
#         for meta in metas
#     )

#     prompt = f"""
# You are comparing two health insurance plans: Medright 2024 vs Seha One 2025.

# User question: {user_query}

# Here are retrieved plan details:
# {context}

# Answer in English, structured as a comparison:
# 1. Medright 2024 coverage
# 2. Seha One 2025 coverage
# 3. Key differences and which one is better
# """

#     response = client.generate_text(model=MODEL_NAME, prompt=prompt)

#     return {
#         "question": user_query,
#         "context_used": context,
#         "answer": response.text
#     }

#_____________________right one

# import os
# from fastapi import APIRouter, HTTPException
# from pydantic import BaseModel
# import google.generativeai as genai

# from chroma_functionalities import get_chroma_collection
# from utils.enums import Endpoints

# # ✅ Always define gemini_model
# gemini_model = None

# # ✅ Configure Gemini
# GEMINI_KEY = os.getenv("GEMINI_API_KEY")
# if GEMINI_KEY:
#     genai.configure(api_key=GEMINI_KEY)
#     try:
#         gemini_model = genai.GenerativeModel("models/gemini-1.5-flash")  # fast + stable
#     except Exception as e:
#         print(f"[WARN] Could not initialize Gemini model: {e}")


# # ✅ FastAPI Router
# router = APIRouter(prefix=Endpoints.API_PREFIX.value, tags=["RAG"])



# @router.post(Endpoints.ASK_RAG.value)
# async def ask_rag(input: AskRequest):
#     """
#     Retrieval-Augmented Generation (RAG) endpoint.
#     Compares Medright 2024 vs Seha One 2025 coverage based on stored documents.
#     """
#     try:
#         user_query = input.query.strip()
#         if not user_query:
#             raise HTTPException(status_code=400, detail="Query text missing")

#         # 🔹 Retrieve from ChromaDB
#         collection = get_chroma_collection()
#         results = collection.query(
#             query_texts=[user_query],
#             n_results=10,
#             include=["documents", "metadatas"]
#         )

#         docs = results.get("documents", [[]])[0]
#         metas = results.get("metadatas", [[]])[0]

#         # ✅ Handle empty retrievals gracefully
#         if not docs:
#             return {
#                 "question": user_query,
#                 "context_used": "",
#                 "answer": "No relevant information was found in the knowledge base."
#             }

#         # 🔹 Build context
#         context_blocks = []
#         for meta in metas:
#             context_blocks.append(
#                 f"Service: {meta.get('service','')} | "
#                 f"Medright 2024: {meta.get('medright_2024','')} | "
#                 f"Seha One 2025: {meta.get('seha_one_2025','')}"
#             )
#         context = "\n".join(context_blocks)

#         # 🔹 Prompt for Gemini
#         prompt = f"""
# You are comparing two health insurance plans: Medright 2024 vs Seha One 2025.

# User question: {user_query}

# Here are retrieved plan details:
# {context}

# Answer in **English**, structured as a comparison:
# 1. Medright 2024 coverage
# 2. Seha One 2025 coverage
# 3. Key differences and which one is better
# """

#         # 🔹 Call Gemini if available
#         if gemini_model:
#             gemini_response = gemini_model.generate_content(prompt)
#             answer = gemini_response.text
#         else:
#             # Fallback: just return the constructed prompt (debug mode)
#             answer = f"(Gemini not configured)\n\n{prompt}"

#         return {
#             "question": user_query,
#             "context_used": context,
#             "answer": answer
#         }

#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"RAG pipeline failed: {e}")
#____________________________________

# # routers/gemini_router.py
# import os
# from typing import List, Dict, Any
# from fastapi import APIRouter, HTTPException
# from dotenv import load_dotenv
# import google.generativeai as genai

# from dtos.question_request import QuestionRequest
# from dtos.ask_request import AskRequest
# from chroma_functionalities import get_chroma_collection
# from utils.enums import Endpoints

# # --- Load environment variables ---
# load_dotenv()

# # --------- Gemini client (lazy singleton) ---------
# _MODEL_NAME = "models/gemini-1.5-flash"   # stable + fast
# _genai_configured = False
# _model = None

# def _ensure_gemini() -> None:
#     """Configure Gemini client once, only when needed."""
#     global _genai_configured, _model
#     if _genai_configured and _model is not None:
#         return
#     api_key = os.getenv("GEMINI_API_KEY")
#     if not api_key:
#         raise HTTPException(status_code=500, detail="GEMINI_API_KEY is not set.")
#     genai.configure(api_key=api_key)
#     _model = genai.GenerativeModel(_MODEL_NAME)
#     _genai_configured = True

# def _clip_answer(ans: str, limit: int = 2000) -> str:
#     """Trim overly long responses."""
#     ans = (ans or "").strip()
#     if len(ans) > limit:
#         return ans[:limit].rstrip() + "..."
#     return ans

# # ✅ Single router for both endpoints
# router = APIRouter(tags=["Gemini"], prefix=Endpoints.API_PREFIX.value)

# # --------- Plain Gemini Endpoint ---------
# @router.post(Endpoints.ASK_GEMINI.value)
# async def ask_gemini_endpoint(req: QuestionRequest):
#     """
#     Direct Gemini response (no RAG).
#     """
#     try:
#         _ensure_gemini()
#         response = _model.generate_content(req.question)
#         answer = _clip_answer(getattr(response, "text", "") or "")
#         return {"question": req.question, "answer": answer}
#     except HTTPException:
#         raise
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"Error from Gemini API: {str(e)}")

# # --------- RAG Endpoint ---------
# @router.post(Endpoints.ASK_RAG.value)
# async def ask_rag(input: AskRequest):
#     """
#     Retrieval-Augmented Generation (RAG).
#     Compare Medright 2024 vs Seha One 2025 using stored ChromaDB documents.
#     """
#     try:
#         user_query = input.query.strip()
#         if not user_query:
#             raise HTTPException(status_code=400, detail="Query text missing.")

#         # 🔹 Retrieve from ChromaDB
#         collection = get_chroma_collection()
#         results = collection.query(
#             query_texts=[user_query],
#             n_results=10,
#             include=["documents", "metadatas"]
#         )

#         docs = results.get("documents", [[]])[0]
#         metas = results.get("metadatas", [[]])[0]

#         if not docs:
#             return {
#                 "question": user_query,
#                 "context_used": "",
#                 "answer": "No relevant information was found in the knowledge base."
#             }

#         # 🔹 Build context from docs + metadata (generic, works with any keys)
#         context_blocks = []
#         for doc, meta in zip(docs, metas):
#             meta = meta or {}
#             kv_pairs = [f"{k}: {v}" for k, v in meta.items() if v]
#             context_blocks.append(" | ".join(kv_pairs) + f"\nTEXT: {doc}")
#         context = "\n---\n".join(context_blocks)

#         # 🔹 Prompt for Gemini
#         prompt = f"""
# You are comparing two health insurance plans: Medright 2024 vs Seha One 2025.

# Question: {user_query}

# Context (retrieved from documents):
# {context}

# Answer in **English**, structured clearly:
# 1. Medright 2024 coverage
# 2. Seha One 2025 coverage
# 3. Key differences and which plan is better
# """

#         # 🔹 Call Gemini
#         _ensure_gemini()
#         gemini_response = _model.generate_content(prompt)
#         answer = _clip_answer(getattr(gemini_response, "text", "") or "")

#         return {"question": user_query, "context_used": context, "answer": answer}

#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"RAG pipeline failed: {str(e)}")

# # routers/gemini_router.py
# import os
# from typing import List, Dict, Any

# from fastapi import APIRouter, HTTPException
# from dotenv import load_dotenv
# import google.generativeai as genai

# from dtos.question_request import QuestionRequest
# from dtos.ask_request import AskRequest
# from chroma_functionalities import get_chroma_collection
# from utils.enums import Endpoints

# # --- Load env ---
# load_dotenv()

# router = APIRouter(prefix=Endpoints.API_PREFIX.value, tags=["Gemini"])

# # --------- Gemini setup ---------
# gemini_model = None
# GEMINI_KEY = os.getenv("GEMINI_API_KEY")
# if GEMINI_KEY:
#     genai.configure(api_key=GEMINI_KEY)
#     try:
#         gemini_model = genai.GenerativeModel("models/gemini-1.5-flash")
#     except Exception as e:
#         print(f"[WARN] Could not initialize Gemini model: {e}")


# # --------- Helpers ---------
# def clip_context(text: str, limit: int = 3000) -> str:
#     """Keep context small for Gemini but full debug is returned."""
#     return text[:limit] + ("..." if len(text) > limit else "")


# def _format_context(metas: List[Dict[str, Any]]) -> str:
#     """Format retrieval metadata into concise context lines."""
#     blocks = []
#     for meta in metas:
#         blocks.append(
#             f"Service: {meta.get('service','')} | "
#             f"Medright 2024: {meta.get('medright_2024','')} | "
#             f"Seha One 2025: {meta.get('seha_one_2025','')}"
#         )
#     return "\n".join(blocks)


# # --------- Endpoints ---------
# @router.post(Endpoints.ASK_GEMINI.value)
# async def ask_gemini_endpoint(req: QuestionRequest):
#     """Direct Gemini call without RAG."""
#     try:
#         if not gemini_model:
#             raise HTTPException(status_code=500, detail="Gemini model not configured.")

#         response = gemini_model.generate_content(req.question)
#         return {"question": req.question, "answer": response.text}
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"Gemini error: {e}")


# @router.post(Endpoints.ASK_RAG.value)
# async def ask_rag(input: AskRequest):
#     """RAG endpoint: retrieve from Chroma + send to Gemini."""
#     try:
#         user_query = input.query.strip()
#         if not user_query:
#             raise HTTPException(status_code=400, detail="Query text missing")

#         # --- Retrieve from ChromaDB
#         collection = get_chroma_collection()
#         results = collection.query(
#             query_texts=[user_query],
#             n_results=10,
#             include=["documents", "metadatas"]
#         )

#         docs = results.get("documents", [[]])[0]
#         metas = results.get("metadatas", [[]])[0]

#         if not docs:
#             return {
#                 "question": user_query,
#                 "context_used": "",
#                 "answer": "No relevant information found."
#             }

#         # --- Build context
#         full_context = _format_context(metas)
#         context_for_model = clip_context(full_context, 3000)

#         # --- Strict prompt with forced table format
#         prompt = f"""
# You are comparing two health insurance plans: Medright 2024 vs Seha One 2025.

# User question: {user_query}

# Here are retrieved plan details (may be incomplete, only use what is given):
# {context_for_model}

# Answer in **English** using this exact structure:

# ### Verdict
# A one-line plain English summary of which plan is better (or if they are similar).

# ### Comparison Table
# Output in **Markdown table format** with **exactly 3 columns**:
# `Attribute | Medright 2024 | Seha One 2025`

# - Each row = one attribute (coverage limit, ceiling, medication, exclusions, etc.)
# - If info is missing, write `Not stated`

# ### Notes
# - 2–4 bullet points with extra important conditions, exceptions, or clarifications.
# - Do NOT invent information not present in context.
# """

#         if gemini_model:
#             gemini_response = gemini_model.generate_content(prompt)
#             answer = gemini_response.text
#         else:
#             answer = f"(Gemini not configured)\n\n{prompt}"

#         return {
#             "question": user_query,
#             "context_used": full_context,  # full debug
#             "answer": answer
#         }

#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"RAG pipeline failed: {e}")

# routers/gemini_router.py
import os
from typing import List, Dict, Any

from fastapi import APIRouter, HTTPException
from dotenv import load_dotenv
import google.generativeai as genai

from dtos.question_request import QuestionRequest
from dtos.ask_request import AskRequest
from chroma_functionalities import get_chroma_collection
from utils.enums import Endpoints

# --- Load env ---
load_dotenv()

router = APIRouter(prefix=Endpoints.API_PREFIX.value, tags=["Gemini"])

# --------- Gemini setup ---------
gemini_model = None
GEMINI_KEY = os.getenv("GEMINI_API_KEY")
if GEMINI_KEY:
    genai.configure(api_key=GEMINI_KEY)
    try:
        gemini_model = genai.GenerativeModel("models/gemini-1.5-flash")
    except Exception as e:
        print(f"[WARN] Could not initialize Gemini model: {e}")


# --------- Helpers ---------
def clip_context(text: str, limit: int = 3000) -> str:
    """Keep context small for Gemini but full debug is returned."""
    return text[:limit] + ("..." if len(text) > limit else "")

def _format_context(metas: List[Dict[str, Any]]) -> str:
    """
    Format retrieval metadata into concise context lines.
    Uses human-friendly column headers if available.
    """
    blocks = []
    for meta in metas:
        # headers saved as string like: "Service, Medright 2024, Seha One 2025"
        headers_str = meta.get("headers", "")
        headers = [h.strip() for h in headers_str.split(",")] if headers_str else []

        cols = []
        for h in headers:
            if h.lower() == "service":
                continue  # skip repeating "Service" inside the row
            val = meta.get(h, "")
            cols.append(f"{h}: {val if val else 'Not stated'}")

        cols_str = " | ".join(cols) if cols else "No columns"
        blocks.append(f"Service: {meta.get('service','')} | {cols_str}")

    return "\n".join(blocks)


# --------- Endpoints ---------
@router.post(Endpoints.ASK_GEMINI.value)
async def ask_gemini_endpoint(req: QuestionRequest):
    """Direct Gemini call without RAG."""
    try:
        if not gemini_model:
            raise HTTPException(status_code=500, detail="Gemini model not configured.")

        response = gemini_model.generate_content(req.question)
        return {"question": req.question, "answer": response.text}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Gemini error: {e}")


@router.post(Endpoints.ASK_RAG.value)
async def ask_rag(input: AskRequest):
    """RAG endpoint: retrieve from Chroma + send to Gemini."""
    try:
        user_query = input.query.strip()
        if not user_query:
            raise HTTPException(status_code=400, detail="Query text missing")

        # --- Retrieve from ChromaDB
        collection = get_chroma_collection()
        results = collection.query(
            query_texts=[user_query],
            n_results=10,
            include=["documents", "metadatas"]
        )

        docs = results.get("documents", [[]])[0]
        metas = results.get("metadatas", [[]])[0]

        if not docs:
            return {
                "question": user_query,
                "context_used": "",
                "answer": "No relevant information found."
            }

        # --- Build context
        full_context = _format_context(metas)
        context_for_model = clip_context(full_context, 3000)

        # --- Strict prompt with dynamic table support
#         prompt = f"""
# You are comparing health insurance plan details extracted from tables.

# User question: {user_query}

# Here are retrieved plan details (may be incomplete, only use what is given):
# {context_for_model}

# Answer in **English** using this exact structure:

# ### Verdict
# A one-line plain English summary of which plan is better (or if they are similar).

# ### Comparison Table
# Output in **Markdown table format**.

# - The first column is always `Attribute`.
# - The next columns should match the extracted ones (col_1, col_2, col_3, ...).
# - Each row = one attribute (coverage limit, ceiling, medication, exclusions, etc.).
# - If info is missing, write `Not stated`.

# ### Notes
# - 2–4 bullet points with extra important conditions, exceptions, or clarifications.
# - Do NOT invent information not present in context.
# """
# --- Strict prompt with dynamic table support
        prompt = f"""
You are comparing health insurance plan details extracted from tables.

User question: {user_query}

Here are retrieved plan details (may be incomplete, only use what is given):
{context_for_model}

Answer in **English** using this exact structure:

### Verdict
A one-line plain English summary of which plan is better (or if they are similar).

### Comparison Table
Output in **Markdown table format**.

- The first column is always `Attribute`.
- The next columns should match the plan names extracted from headers 
  (e.g., "Medright 2024", "Seha One 2025") instead of generic col_1, col_2.
- Each row = one attribute (coverage limit, ceiling, medication, exclusions, etc.).
- If info is missing, write `Not stated`.

### Notes
- 2–4 bullet points with extra important conditions, exceptions, or clarifications.
- Do NOT invent information not present in context.
"""

        if gemini_model:
            gemini_response = gemini_model.generate_content(prompt)
            answer = gemini_response.text
        else:
            answer = f"(Gemini not configured)\n\n{prompt}"

        return {
            "question": user_query,
            "context_used": full_context,  # full debug
            "answer": answer
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"RAG pipeline failed: {e}")
