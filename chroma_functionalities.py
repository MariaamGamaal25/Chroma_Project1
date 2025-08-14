import os
import uuid
import chromadb
from chromadb.utils import embedding_functions
from utils.enums import ChromaDBConfig, Messages, MetadataKeys
from utils.logger import setup_logger
from transformers import AutoTokenizer

# -------------------------------
# Logger
# -------------------------------
logger = setup_logger(__name__)

# -------------------------------
# Initialize ChromaDB
# -------------------------------
persist_dir = os.path.join(os.getcwd(), ChromaDBConfig.DB_DIRECTORY)
try:
    if not os.path.isdir(os.path.dirname(persist_dir)):
        logger.error(f"Invalid database directory path: {persist_dir}")
        raise RuntimeError(f"Invalid database directory path: {persist_dir}")
    _client = chromadb.PersistentClient(path=persist_dir)
    logger.info(f"Initialized ChromaDB client at {persist_dir}")
except Exception as e:
    logger.error(f"Failed to initialize ChromaDB client: {str(e)}")
    raise RuntimeError(f"Failed to initialize ChromaDB client: {str(e)}")

try:
    _embedding_func = embedding_functions.SentenceTransformerEmbeddingFunction(
        model_name=ChromaDBConfig.EMBEDDING_MODEL
    )
    logger.info(f"Initialized embedding function: {ChromaDBConfig.EMBEDDING_MODEL}")
except Exception as e:
    logger.error(f"Failed to initialize embedding function: {str(e)}")
    raise RuntimeError(f"Failed to initialize embedding function: {str(e)}")

client = chromadb.PersistentClient(path=ChromaDBConfig.DB_DIRECTORY)

embedding_func = embedding_functions.SentenceTransformerEmbeddingFunction(
    model_name=ChromaDBConfig.EMBEDDING_MODEL
)

collection = client.get_or_create_collection(
    name=ChromaDBConfig.COLLECTION_NAME,
    embedding_function=embedding_func,
    metadata={"hnsw:space": "cosine"}  # cosine similarity
)

# -------------------------------
# Tokenizer-aware chunking
# -------------------------------


tokenizer = AutoTokenizer.from_pretrained(f"sentence-transformers/{ChromaDBConfig.EMBEDDING_MODEL}")

def chunk_text_by_tokens(text: str, max_tokens: int = 300, overlap_tokens: int = 50) -> list[str]:
    """
    Splits text into chunks based on token count for embedding model.

    Args:
        text: Full text string
        max_tokens: Max tokens per chunk
        overlap_tokens: Token overlap between chunks

    Returns:
        List of text chunks
    """
    tokens = tokenizer.encode(text, add_special_tokens=False)
    chunks = []
    start = 0

    while start < len(tokens):
        end = start + max_tokens
        chunk_tokens = tokens[start:end]
        chunk_text = tokenizer.decode(chunk_tokens, skip_special_tokens=True)
        chunks.append(chunk_text.strip())
        start += max_tokens - overlap_tokens

    return [c for c in chunks if c]


def get_chroma_collection():
    """Return or create the ChromaDB collection."""
    try:
        return _client.get_or_create_collection(
            name=ChromaDBConfig.COLLECTION_NAME,
            embedding_function=_embedding_func
        )
    except Exception as e:
        logger.error(f"Failed to get or create collection: {str(e)}")
        raise RuntimeError(f"Failed to get or create collection: {str(e)}")


def ensure_text_file_exists(file_path: str) -> None:
    """Ensure file exists and is not empty."""
    if not os.path.exists(file_path):
        logger.error(Messages.FILE_NOT_FOUND.format(file_path=file_path))
        raise FileNotFoundError(Messages.FILE_NOT_FOUND.format(file_path=file_path))
    if os.path.getsize(file_path) == 0:
        logger.error(f"File '{file_path}' is empty")
        raise ValueError(f"File '{file_path}' is empty")


def read_text_file(file_path: str, max_tokens: int = 300, overlap_tokens: int = 50) -> list[str]:
    """Read file and split into token-based chunks."""
    logger.info(Messages.OPENING_FILE.format(file_path=file_path))
    with open(file_path, "r", encoding="utf-8") as f:
        full_text = f.read()
    chunks = chunk_text_by_tokens(full_text, max_tokens, overlap_tokens)
    logger.info(Messages.READ_LINES.format(count=len(chunks)))
    return chunks


def store_in_collection(collection, chunks: list[str], file_path: str) -> None:
    """Store chunks in ChromaDB."""
    if not chunks:
        logger.info("No documents to add to the collection")
        return
    logger.info(Messages.ADDING_DOCUMENTS)

    ids = [str(uuid.uuid4()) for _ in range(len(chunks))]
    metadatas = [
        {MetadataKeys.LINE_NUMBER: i, MetadataKeys.SOURCE: os.path.basename(file_path)}
        for i in range(len(chunks))
    ]
    collection.add(documents=chunks, ids=ids, metadatas=metadatas)
    logger.info(Messages.DOCUMENTS_ADDED)


def get_collection_documents(collection) -> dict[str, tuple[str, str]]:
    """Return current docs in collection mapped by source+chunk_index."""
    data = collection.get(include=['documents', 'metadatas'])
    return {
        f"{meta['source']}{meta['line_number']}": (doc, id)
        for doc, id, meta in zip(data['documents'], data['ids'], data['metadatas'])
    }


def delete_documents(collection, ids: list[str]) -> None:
    """Delete docs from collection by IDs."""
    if ids:
        logger.info(f"Deleting {len(ids)} outdated documents")
        collection.delete(ids=ids)


def sync_text_file_with_collection(collection, file_path: str, force: bool = False) -> None:
    """
    Synchronize a file with the ChromaDB collection using token-based chunks.
    """
    logger.info(f"Synchronizing collection '{ChromaDBConfig.COLLECTION_NAME}' with file '{file_path}'")
    
    ensure_text_file_exists(file_path)
    new_chunks = read_text_file(file_path)
    if not new_chunks:
        logger.info("No new documents to process")
        return

    if force:
        logger.info(Messages.FORCE_CLEAR_COLLECTION.format(collection_name=ChromaDBConfig.COLLECTION_NAME))
        collection.delete(ids=None, where={})
        store_in_collection(collection, new_chunks, file_path)
        logger.info(Messages.DOCS_ADDED)
        return

    # Get existing docs
    current_docs = get_collection_documents(collection)
    new_docs = {f"{os.path.basename(file_path)}{i}": chunk for i, chunk in enumerate(new_chunks)}

    # Detect changes
    to_delete_ids = [id for key, (_, id) in current_docs.items() if key not in new_docs]
    to_add = [
        (chunk, i) for i, chunk in enumerate(new_chunks)
        if f"{os.path.basename(file_path)}{i}" not in current_docs
        or current_docs[f"{os.path.basename(file_path)}{i}"][0] != chunk
    ]

    # Apply changes
    delete_documents(collection, to_delete_ids)
    if to_add:
        chunks, _ = zip(*to_add)
        store_in_collection(collection, list(chunks), file_path)
        logger.info(Messages.DOCS_ADDED)
    elif not to_delete_ids:
        logger.info(Messages.COLLECTION_NOT_EMPTY)


def initialize_collection():
    """Initialize collection and load default file if empty."""
    try:
        collection = get_chroma_collection()
        if collection.count() > 0:
            logger.info(Messages.COLLECTION_EXISTS_WITH_DATA.format(
                collection_name=ChromaDBConfig.COLLECTION_NAME,
                count=collection.count()
            ))
        else:
            logger.info(Messages.COLLECTION_EXISTS_EMPTY.format(
                collection_name=ChromaDBConfig.COLLECTION_NAME
            ))
            sync_text_file_with_collection(collection, ChromaDBConfig.FILE_PATH)
    except Exception as e:
        logger.error(f"Failed to initialize collection: {str(e)}")
        raise



