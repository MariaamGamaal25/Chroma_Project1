# chroma_functionalities.py
import os
import uuid
from typing import List, Dict

import chromadb
from chromadb.utils import embedding_functions

from utils.enums import ChromaDBConfig, Messages, MetadataKeys
from utils.logger import setup_logger
from utils.file_reader import read_all_text , extract_pdf_service_blocks , extract_docx_service_blocks

logger = setup_logger(__name__)

# ---------- Chroma client & embeddings ----------
persist_dir = os.path.join(os.getcwd(), ChromaDBConfig.DB_DIRECTORY)
if not os.path.isdir(os.path.dirname(persist_dir)):
    raise RuntimeError(f"Invalid database directory path: {persist_dir}")

_client = chromadb.PersistentClient(path=persist_dir)

_embedding_func = embedding_functions.SentenceTransformerEmbeddingFunction(
    model_name=ChromaDBConfig.EMBEDDING_MODEL
)

def get_chroma_collection():
    """Create/retrieve collection with embedding function attached."""
    return _client.get_or_create_collection(
        name=ChromaDBConfig.COLLECTION_NAME,
        embedding_function=_embedding_func
    )

# ---------- Sync helpers ----------
def _ensure_exists(file_path: str) -> None:
    if not os.path.exists(file_path):
        raise FileNotFoundError(Messages.FILE_NOT_FOUND.value + f" '{file_path}'")
    if os.path.getsize(file_path) == 0:
        raise ValueError(f"File '{file_path}' is empty")

def sync_text_file_with_collection(collection, file_path: str, force: bool = False) -> None:
    """
    Extract + parse a file and upsert to ChromaDB.
    Supports PDF table parsing into row + service docs.
    If force=True, old chunks for this filename are deleted first.
    """
    _ensure_exists(file_path)
    logger.info(f"Processing file: {file_path}")

    if force:
        try:
            collection.delete(where={MetadataKeys.FILENAME.value: os.path.basename(file_path)})
            logger.info("Old docs removed (force=True).")
        except Exception:
            pass

    # Try table extraction first
    docs = []
    if file_path.lower().endswith(".pdf"):
        docs = extract_pdf_service_blocks(file_path)

    if not docs:  # fallback = plain text
        text = read_all_text(file_path)
        if not text.strip():
            logger.warning("No text extracted.")
            return
        docs = [{
            "id": str(uuid.uuid4()),
            "text": text,
            "metadata": {
                MetadataKeys.FILENAME.value: os.path.basename(file_path),
                MetadataKeys.SOURCE.value: os.path.basename(file_path),
                "section": "FullText",
                "doc_type": "full"
            }
        }]

    collection.add(
        ids=[c["id"] for c in docs],
        documents=[c["text"] for c in docs],
        metadatas=[c["metadata"] for c in docs],
    )
    logger.info(Messages.DOCUMENTS_ADDED.value)


def sync_text_file_with_collection(collection, file_path: str, force: bool = False) -> None:
    """
    Extract + parse a file and upsert to ChromaDB.
    Supports:
      - PDF: table parsing into row + service docs
      - DOCX: same structure using extract_docx_service_blocks
      - TXT: fallback full text
    If force=True, old chunks for this filename are deleted first.
    """
    _ensure_exists(file_path)
    logger.info(f"Processing file: {file_path}")

    if force:
        try:
            collection.delete(where={MetadataKeys.FILENAME.value: os.path.basename(file_path)})
            logger.info("Old docs removed (force=True).")
        except Exception:
            pass

    # ---- Extract content depending on file type ----
    docs: List[Dict] = []
    if file_path.lower().endswith(".pdf"):
        docs = extract_pdf_service_blocks(file_path)
    elif file_path.lower().endswith(".docx"):
        docs = extract_docx_service_blocks(file_path)

    # ---- Fallback: plain text reader ----
    if not docs:
        text = read_all_text(file_path)
        if not text.strip():
            logger.warning("No text extracted.")
            return
        docs = [{
            "id": str(uuid.uuid4()),
            "text": text,
            "metadata": {
                MetadataKeys.FILENAME.value: os.path.basename(file_path),
                MetadataKeys.SOURCE.value: os.path.basename(file_path),
                "section": "FullText",
                "doc_type": "full"
            }
        }]

    # ---- Insert into ChromaDB ----
    collection.add(
        ids=[c["id"] for c in docs],
        documents=[c["text"] for c in docs],
        metadatas=[c["metadata"] for c in docs],
    )
    logger.info(Messages.DOCUMENTS_ADDED.value)


