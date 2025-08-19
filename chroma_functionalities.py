import os
import uuid
import chromadb
from chromadb.utils import embedding_functions
from utils.enums import ChromaDBConfig, Messages, MetadataKeys
from utils.logger import setup_logger
from transformers import AutoTokenizer

logger = setup_logger(__name__)

# --- Initialize ChromaDB client ---
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

# --- Initialize embedding function ---
try:
    _embedding_func = embedding_functions.SentenceTransformerEmbeddingFunction(
        model_name=ChromaDBConfig.EMBEDDING_MODEL
    )
    logger.info(f"Initialized embedding function: {ChromaDBConfig.EMBEDDING_MODEL}")
except Exception as e:
    logger.error(f"Failed to initialize embedding function: {str(e)}")
    raise RuntimeError(f"Failed to initialize embedding function: {str(e)}")

# Direct client and collection reference
client = chromadb.PersistentClient(path=ChromaDBConfig.DB_DIRECTORY)
embedding_func = embedding_functions.SentenceTransformerEmbeddingFunction(
    model_name=ChromaDBConfig.EMBEDDING_MODEL
)
collection = client.get_or_create_collection(
    name=ChromaDBConfig.COLLECTION_NAME,
    embedding_function=embedding_func,
    metadata={"hnsw:space": "cosine"}  
)

# Tokenizer for chunking text
tokenizer = AutoTokenizer.from_pretrained(
    f"sentence-transformers/{ChromaDBConfig.EMBEDDING_MODEL}"
)


def chunk_text_by_tokens(text: str, max_tokens: int = 300, overlap_tokens: int = 50) -> list[str]:
    """
    Split a given text into chunks based on token count.

    This ensures the chunks are suitable for embedding models with token limits.

    Args:
        text (str): The full text string to be chunked.
        max_tokens (int): Maximum number of tokens per chunk.
        overlap_tokens (int): Number of overlapping tokens between consecutive chunks.

    Returns:
        list[str]: A list of text chunks that fit within the token constraints.
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
    """
    Retrieve or create the ChromaDB collection.

    Returns:
        chromadb.api.models.Collection.Collection: The ChromaDB collection object.

    Raises:
        RuntimeError: If the collection cannot be retrieved or created.
    """
    try:
        return _client.get_or_create_collection(
            name=ChromaDBConfig.COLLECTION_NAME,
            embedding_function=_embedding_func
        )
    except Exception as e:
        logger.error(f"Failed to get or create collection: {str(e)}")
        raise RuntimeError(f"Failed to get or create collection: {str(e)}")


def ensure_text_file_exists(file_path: str) -> None:
    """
    Ensure the specified text file exists and is not empty.

    Args:
        file_path (str): Path to the text file.

    Raises:
        FileNotFoundError: If the file does not exist.
        ValueError: If the file is empty.
    """
    if not os.path.exists(file_path):
        logger.error(Messages.FILE_NOT_FOUND.format(file_path=file_path))
        raise FileNotFoundError(Messages.FILE_NOT_FOUND.format(file_path=file_path))
    if os.path.getsize(file_path) == 0:
        logger.error(f"File '{file_path}' is empty")
        raise ValueError(f"File '{file_path}' is empty")


def read_text_file(file_path: str, max_tokens: int = 300, overlap_tokens: int = 50) -> list[str]:
    """
    Read a text file and split it into token-based chunks.

    Args:
        file_path (str): Path to the text file.
        max_tokens (int): Maximum tokens per chunk.
        overlap_tokens (int): Tokens overlapping between chunks.

    Returns:
        list[str]: List of chunked strings from the file.
    """
    logger.info(Messages.OPENING_FILE.format(file_path=file_path))
    with open(file_path, "r", encoding="utf-8") as f:
        full_text = f.read()
    chunks = chunk_text_by_tokens(full_text, max_tokens, overlap_tokens)
    logger.info(Messages.READ_LINES.format(count=len(chunks)))
    return chunks




def store_in_collection(collection, chunks: list[str], file_path: str) -> None:
    """
    Store a list of text chunks into a ChromaDB collection.

    Args:
        collection (chromadb.api.models.Collection.Collection): ChromaDB collection object.
        chunks (list[str]): List of text chunks to store.
        file_path (str): Source file path for metadata.
    """
    if not chunks:
        logger.info("No documents to add to the collection")
        return

    logger.info(Messages.ADDING_DOCUMENTS)

    ids = [str(uuid.uuid4()) for _ in range(len(chunks))]
    metadatas = [
        {
            MetadataKeys.LINE_NUMBER: i,
            MetadataKeys.SOURCE: file_path,  # full path for consistency with delete()
        }
        for i in range(len(chunks))
    ]

    collection.add(documents=chunks, ids=ids, metadatas=metadatas)
    logger.info(Messages.DOCUMENTS_ADDED)



def get_collection_documents(collection) -> dict[str, tuple[str, str]]:
    """
    Retrieve all documents from a ChromaDB collection.

    Args:
        collection (chromadb.api.models.Collection.Collection): ChromaDB collection object.

    Returns:
        dict[str, tuple[str, str]]: Mapping of "source+chunk_index" to (document text, document ID).
    """
    data = collection.get(include=['documents', 'metadatas'])
    return {
        f"{meta['source']}{meta['line_number']}": (doc, id)
        for doc, id, meta in zip(data['documents'], data['ids'], data['metadatas'])
    }


def delete_documents(collection, ids: list[str]) -> None:
    """
    Delete documents from the collection by their IDs.

    Args:
        collection (chromadb.api.models.Collection.Collection): ChromaDB collection object.
        ids (list[str]): List of document IDs to delete.
    """
    if ids:
        logger.info(f"Deleting {len(ids)} outdated documents")
        collection.delete(ids=ids)




def sync_text_file_with_collection(collection, file_path: str, force: bool = False) -> None:
    """
    Store a text file's content into the ChromaDB collection.

    - New file: always adds chunks (even duplicates).
    - Same file (with force=True): deletes old chunks of that file, then adds updated ones.
    """
    logger.info(f"Processing file '{file_path}' into collection '{ChromaDBConfig.COLLECTION_NAME}'")

    ensure_text_file_exists(file_path)
    new_chunks = read_text_file(file_path)
    if not new_chunks:
        logger.info("No new documents to process")
        return

    # If force=True → remove existing chunks from this file
    if force:
        logger.info(f"Force mode ON -> deleting old chunks for file: {file_path}")
        try:
            collection.delete(where={"source": file_path})
            logger.info(f"Old chunks for file '{file_path}' deleted successfully")
        except Exception as e:
            logger.warning(f"No existing chunks found for file '{file_path}': {str(e)}")

    # Always add new chunks (with file metadata)
    store_in_collection(collection, new_chunks, file_path)
    logger.info(Messages.DOCS_ADDED)





def initialize_collection():
    """
    Initialize the ChromaDB collection and load a default file if empty.

    If the collection already contains documents, it logs the count.
    If empty, it loads data from the configured file path.

    Raises:
        RuntimeError: If initialization fails.
    """
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



