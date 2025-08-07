# import os
# import chromadb
# from chromadb.utils import embedding_functions
# from utils.enums import ChromaDBConfig, Messages, MetadataKeys
# import uuid
# from utils.logger import setup_logger

# # Initialize logger
# logger = setup_logger(__name__)

# # Module-level initialization of ChromaDB client and embedding function
# persist_dir = os.path.join(os.getcwd(), ChromaDBConfig.DB_DIRECTORY)
# try:
#     if not os.path.isdir(os.path.dirname(persist_dir)):
#         logger.error(f"Invalid database directory path: {persist_dir}")
#         raise RuntimeError(f"Invalid database directory path: {persist_dir}")
#     _client = chromadb.PersistentClient(path=persist_dir)
#     logger.info(f"Initialized ChromaDB client at {persist_dir}")
# except Exception as e:
#     logger.error(f"Failed to initialize ChromaDB client: {str(e)}")
#     raise RuntimeError(f"Failed to initialize ChromaDB client: {str(e)}")

# try:
#     _embedding_func = embedding_functions.SentenceTransformerEmbeddingFunction(
#         model_name=ChromaDBConfig.EMBEDDING_MODEL
#     )
#     logger.info(f"Initialized embedding function: {ChromaDBConfig.EMBEDDING_MODEL}")
# except Exception as e:
#     logger.error(f"Failed to initialize embedding function: {str(e)}")
#     raise RuntimeError(f"Failed to initialize embedding function: {str(e)}")

# def get_chroma_collection():
#     """
#     Returns the ChromaDB 'text_data' collection, using the pre-initialized client and embedding function.
    
#     Returns:
#         ChromaDB collection instance.
    
#     Raises:
#         RuntimeError: If the collection cannot be accessed or created.
#     """
#     try:
#         collection = _client.get_or_create_collection(
#             name=ChromaDBConfig.COLLECTION_NAME,
#             embedding_function=_embedding_func
#         )
#         return collection
#     except Exception as e:
#         logger.error(f"Failed to get or create collection: {str(e)}")
#         raise RuntimeError(f"Failed to get or create collection: {str(e)}")

# def initialize_collection():
#     """
#     Initializes the ChromaDB collection and populates it with data from the default file
#     if the collection is empty.
#     """
#     try:
#         collection = get_chroma_collection()
#         if collection.count() > 0:
#             logger.info(Messages.COLLECTION_EXISTS_WITH_DATA.format(
#                 collection_name=ChromaDBConfig.COLLECTION_NAME,
#                 count=collection.count()
#             ))
#         else:
#             logger.info(Messages.COLLECTION_EXISTS_EMPTY.format(
#                 collection_name=ChromaDBConfig.COLLECTION_NAME
#             ))
#             store_text_file_once(collection, ChromaDBConfig.FILE_PATH)
#     except Exception as e:
#         logger.error(f"Failed to initialize collection: {str(e)}")
#         raise

# def ensure_text_file_exists(file_path: str) -> None:
#     """
#     Checks if the text file exists; raises an error if it does not.
    
#     Args:
#         file_path: Path to the text file.
        
#     Raises:
#         FileNotFoundError: If the specified file does not exist.
#     """
#     if not os.path.exists(file_path):
#         logger.error(Messages.FILE_NOT_FOUND.format(file_path=file_path))
#         raise FileNotFoundError(Messages.FILE_NOT_FOUND.format(file_path=file_path))

# def read_text_file(file_path: str) -> list[str]:
#     """
#     Reads the text file and returns a list of non-empty lines.
    
#     Args:
#         file_path: Path to the text file.
        
#     Returns:
#         List of non-empty lines from the file.
#     """
#     logger.info(Messages.OPENING_FILE.format(file_path=file_path))
#     with open(file_path, "r", encoding="utf-8") as f:
#         lines = [line.strip() for line in f if line.strip()]
#     logger.info(Messages.READ_LINES.format(count=len(lines)))
#     return lines

# def store_in_collection(collection, lines: list[str], file_path: str) -> None:
#     """
#     Stores the provided lines in the ChromaDB collection with UUID4-generated IDs and metadata.
    
#     Args:
#         collection: ChromaDB collection instance.
#         lines: List of text lines to store.
#         file_path: Path to the source file for metadata.
#     """
#     logger.info(Messages.ADDING_DOCUMENTS)
#     ids = [str(uuid.uuid4()) for _ in range(len(lines))]
#     metadatas = [{MetadataKeys.LINE_NUMBER: i, MetadataKeys.SOURCE: file_path} for i in range(len(lines))]
#     collection.add(
#         documents=lines,
#         ids=ids,
#         metadatas=metadatas
#     )
#     logger.info(Messages.DOCUMENTS_ADDED)

# def store_text_file_once(collection, file_path: str, force: bool = False) -> None:
#     """
#     Synchronizes a text file with the ChromaDB collection.
    
#     Args:
#         collection: ChromaDB collection instance.
#         file_path: Path to the text file.
#         force: If True, clears the collection and reprocesses the file.
#     """
#     if force:
#         logger.info(Messages.FORCE_CLEAR_COLLECTION.format(collection_name=ChromaDBConfig.COLLECTION_NAME))
#         collection.delete(ids=None, where={})
#         logger.info(Messages.COLLECTION_EMPTY)
#         ensure_text_file_exists(file_path)
#         lines = read_text_file(file_path)
#         store_in_collection(collection, lines, file_path)
#         logger.info(Messages.DOCS_ADDED)
#     else:
#         # Get current collection data
#         current_data = collection.get(include=['documents', 'metadatas'])
#         current_docs = {meta['source'] + str(meta['line_number']): (doc, id) 
#                         for doc, id, meta in zip(current_data['documents'], current_data['ids'], current_data['metadatas'])}
        
#         # Read new file data
#         ensure_text_file_exists(file_path)
#         new_lines = read_text_file(file_path)
#         new_docs = {file_path + str(i): line for i, line in enumerate(new_lines)}
        
#         # Find documents to add or delete
#         to_add_lines = []
#         to_add_indices = []
#         to_delete_ids = [id for key, (doc, id) in current_docs.items() if key not in new_docs]
        
#         for i, line in enumerate(new_lines):
#             key = file_path + str(i)
#             if key not in current_docs or current_docs[key][0] != line:
#                 to_add_lines.append(line)
#                 to_add_indices.append(i)
        
#         # Delete outdated documents
#         if to_delete_ids:
#             logger.info(f"Deleting {len(to_delete_ids)} outdated documents")
#             collection.delete(ids=to_delete_ids)
        
#         # Add new or updated documents
#         if to_add_lines:
#             logger.info(f"Adding {len(to_add_lines)} new or updated documents")
#             ids = [str(uuid.uuid4()) for _ in range(len(to_add_lines))]
#             metadatas = [{MetadataKeys.LINE_NUMBER: i, MetadataKeys.SOURCE: file_path} for i in to_add_indices]
#             collection.add(documents=to_add_lines, ids=ids, metadatas=metadatas)
#             logger.info(Messages.DOCUMENTS_ADDED)
        
#         if not to_add_lines and not to_delete_ids:
#             logger.info(Messages.COLLECTION_NOT_EMPTY)

import os
import chromadb
from chromadb.utils import embedding_functions
from utils.enums import ChromaDBConfig, Messages, MetadataKeys
import uuid
from utils.logger import setup_logger

# Initialize logger
logger = setup_logger(__name__)

# Module-level initialization of ChromaDB client and embedding function
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

def get_chroma_collection():
    """
    Returns the ChromaDB 'text_data' collection, using the pre-initialized client and embedding function.
    
    Returns:
        ChromaDB collection instance.
    
    Raises:
        RuntimeError: If the collection cannot be accessed or created.
    """
    try:
        collection = _client.get_or_create_collection(
            name=ChromaDBConfig.COLLECTION_NAME,
            embedding_function=_embedding_func
        )
        return collection
    except Exception as e:
        logger.error(f"Failed to get or create collection: {str(e)}")
        raise RuntimeError(f"Failed to get or create collection: {str(e)}")

def initialize_collection():
    """
    Initializes the ChromaDB collection and populates it with data from the default file
    if the collection is empty.
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
            store_text_file_once(collection, ChromaDBConfig.FILE_PATH)
    except Exception as e:
        logger.error(f"Failed to initialize collection: {str(e)}")
        raise

def ensure_text_file_exists(file_path: str) -> None:
    """
    Checks if the text file exists and is not empty; raises an error if invalid.
    
    Args:
        file_path: Path to the text file.
        
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

def read_text_file(file_path: str) -> list[str]:
    """
    Reads the text file and returns a list of non-empty lines.
    
    Args:
        file_path: Path to the text file.
        
    Returns:
        List of non-empty lines from the file.
    """
    logger.info(Messages.OPENING_FILE.format(file_path=file_path))
    with open(file_path, "r", encoding="utf-8") as f:
        lines = [line.strip() for line in f if line.strip()]
    logger.info(Messages.READ_LINES.format(count=len(lines)))
    return lines

def store_in_collection(collection, lines: list[str], file_path: str) -> None:
    """
    Stores the provided lines in the ChromaDB collection with UUID4-generated IDs and metadata.
    
    Args:
        collection: ChromaDB collection instance.
        lines: List of text lines to store.
        file_path: Path to the source file for metadata.
    """
    if not lines:
        logger.info("No documents to add to the collection")
        return
    logger.info(Messages.ADDING_DOCUMENTS)
    ids = [str(uuid.uuid4()) for _ in range(len(lines))]
    metadatas = [{MetadataKeys.LINE_NUMBER: i, MetadataKeys.SOURCE: file_path} for i in range(len(lines))]
    collection.add(
        documents=lines,
        ids=ids,
        metadatas=metadatas
    )
    logger.info(Messages.DOCUMENTS_ADDED)

def get_collection_documents(collection) -> dict[str, tuple[str, str]]:
    """
    Retrieves current documents from the collection, keyed by source and line number.
    
    Args:
        collection: ChromaDB collection instance.
        
    Returns:
        Dictionary mapping source+line_number to (document, id).
    """
    data = collection.get(include=['documents', 'metadatas'])
    return {
        f"{meta['source']}{meta['line_number']}": (doc, id)
        for doc, id, meta in zip(data['documents'], data['ids'], data['metadatas'])
    }

def delete_documents(collection, ids: list[str]) -> None:
    """
    Deletes documents from the collection by their IDs.
    
    Args:
        collection: ChromaDB collection instance.
        ids: List of document IDs to delete.
    """
    if ids:
        logger.info(f"Deleting {len(ids)} outdated documents")
        collection.delete(ids=ids)

def store_text_file_once(collection, file_path: str, force: bool = False) -> None:
    """
    Synchronizes a text file with the ChromaDB collection, updating only necessary documents.
    
    Args:
        collection: ChromaDB collection instance.
        file_path: Path to the text file.
        force: If True, clears the collection and fully reprocesses the file.
    """
    logger.info(f"Synchronizing collection '{ChromaDBConfig.COLLECTION_NAME}' with file '{file_path}'")
    
    # Validate and read file
    ensure_text_file_exists(file_path)
    new_lines = read_text_file(file_path)
    if not new_lines:
        logger.info("No new documents to process")
        return
    
    if force:
        logger.info(Messages.FORCE_CLEAR_COLLECTION.format(collection_name=ChromaDBConfig.COLLECTION_NAME))
        collection.delete(ids=None, where={})
        store_in_collection(collection, new_lines, file_path)
        logger.info(Messages.DOCS_ADDED)
        return
    
    # Get current and new documents
    current_docs = get_collection_documents(collection)
    new_docs = {f"{file_path}{i}": line for i, line in enumerate(new_lines)}
    
    # Identify documents to delete and add
    to_delete_ids = [id for key, (_, id) in current_docs.items() if key not in new_docs]
    to_add = [
        (line, i) for i, line in enumerate(new_lines)
        if f"{file_path}{i}" not in current_docs or current_docs[f"{file_path}{i}"][0] != line
    ]
    
    # Perform updates
    delete_documents(collection, to_delete_ids)
    if to_add:
        lines, indices = zip(*to_add) if to_add else ([], [])
        store_in_collection(collection, list(lines), file_path)
        logger.info(Messages.DOCS_ADDED)
    elif not to_delete_ids:
        logger.info(Messages.COLLECTION_NOT_EMPTY)