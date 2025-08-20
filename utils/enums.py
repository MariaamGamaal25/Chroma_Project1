# # # utils/enums.py
# # class ChromaDBConfig:
# #     COLLECTION_NAME = "text_data"
# #     DB_DIRECTORY = "RAG_db"
# #     EMBEDDING_MODEL = "all-MiniLM-L6-v2"
# #     FILE_PATH = "raw_data\data_file.txt"

# # class Messages:
# #     APP_RUNNING = "ChromaDB FastAPI app is running!"
# #     DOC_NOT_FOUND = "Document not found"
# #     DOC_DELETED = "Document deleted successfully."
# #     ALL_DOCS_DELETED = "Successfully deleted all documents."
# #     DELETE_FAILED = "Failed to delete all documents."
# #     FILE_NOT_FOUND = "File not found."
# #     COLLECTION_EMPTY = "Collection is empty. Adding new documents..."
# #     DOCS_ADDED = "Documents successfully added to the collection."
# #     COLLECTION_NOT_EMPTY = "Collection already contains data. Skipping initialization."
# #     COLLECTION_EXISTS_WITH_DATA = "Collection already exists with documents. Skipping initialization."
# #     COLLECTION_EXISTS_EMPTY = "Collection  exists but is empty. Populating with data."
# #     COLLECTION_NOT_EXISTS = "Collection '{collection_name}' does not exist. Creating and populating with data."
# #     OPENING_FILE = "Opening file: {file_path}"
# #     READ_LINES = "Read non-empty lines from the file."
# #     ADDING_DOCUMENTS = "Adding documents to the collection..."
# #     DOCUMENTS_ADDED = "Documents added to the collection."
# #     FORCE_CLEAR_COLLECTION = "Force mode enabled. Clearing collection."
# #     FILE_UPLOADED = "File successfully processed and stored in collection."
# #     INVALID_FILE_TYPE = "Only .txt files are supported."
# #     ERROR_GENERAL = "An error occurred"
# #     ERROR_DELETION = "An error occurred during deletion"
# #     ERROR_FILE_UPLOAD = "An error occurred during file upload"
# #     DATABASE_DROPPED = "Database directory  successfully deleted."
# #     DATABASE_NOT_FOUND = "Database directory  does not exist."

# # class MetadataKeys:
# #     LINE_NUMBER = "line_number"
# #     SOURCE = "source"

# # class Endpoints:
# #     ROOT = "/"
# #     DATA = "/data"
# #     DATA_BY_ID = "/data/{doc_id}"
# #     RAW_DATA = "/raw_data"
# #     UPLOAD_TEXT_FILE = "/upload-text-file"
# #     DROP_DATABASE = "/drop-database"

# # utils/enums.py

# class ChromaDBConfig:
#     """Configuration values for ChromaDB."""
#     COLLECTION_NAME = "text_data"       # Default collection name
#     DB_DIRECTORY = "RAG_db"             # Directory for persistence
#     EMBEDDING_MODEL = "all-MiniLM-L6-v2"  # Model for embeddings
#     FILE_PATH = "raw_data/data_file.txt"  # Default text file path


# class Messages:
#     """Standard response and log messages."""
#     # General
#     APP_RUNNING = "ChromaDB FastAPI app is running!"
#     ERROR_GENERAL = "An error occurred"
#     ERROR_DELETION = "An error occurred during deletion"
#     ERROR_FILE_UPLOAD = "An error occurred during file upload"

#     # File & Document Handling
#     FILE_NOT_FOUND = "File not found."
#     FILE_UPLOADED = "File successfully processed and stored in collection."
#     INVALID_FILE_TYPE = "Invalid file type. Only .txt, .pdf, and .docx are supported."

#     # Collection Handling
#     COLLECTION_EMPTY = "Collection is empty. Adding new documents..."
#     COLLECTION_NOT_EMPTY = "Collection already contains data. Skipping initialization."
#     COLLECTION_EXISTS_WITH_DATA = "Collection already exists with documents. Skipping initialization."
#     COLLECTION_EXISTS_EMPTY = "Collection exists but is empty. Populating with data."
#     COLLECTION_NOT_EXISTS = "Collection '{collection_name}' does not exist. Creating and populating with data."
#     COLLECTION_NOT_FOUND = "Collection not found."
#     COLLECTION_DELETE_SUCCESS = "Collection deleted successfully."

#     # Document Handling
#     DOC_NOT_FOUND = "Document not found"
#     DOC_DELETED = "Document deleted successfully."
#     ALL_DOCS_DELETED = "Successfully deleted all documents."
#     DELETE_FAILED = "Failed to delete all documents."
#     DOCS_ADDED = "Documents successfully added to the collection."
#     DOCUMENTS_ADDED = "Documents added to the collection."

#     # Logs
#     OPENING_FILE = "Opening file: {file_path}"
#     READ_LINES = "Read non-empty lines from the file."
#     ADDING_DOCUMENTS = "Adding documents to the collection..."
#     FORCE_CLEAR_COLLECTION = "Force mode enabled. Clearing collection."

#     # Database
#     DATABASE_DROPPED = "Database directory successfully deleted."
#     DATABASE_NOT_FOUND = "Database directory does not exist."


# # class MetadataKeys:
# #     """Metadata keys stored in ChromaDB."""
# #     LINE_NUMBER = "line_number"   # For TXT-based ingestion
# #     SOURCE = "source"             # Data source (e.g., file path)
# #     FILENAME = "filename"         # Original filename
# #     SECTION = "section"           # Section header (e.g., Dental, Optical, etc.)
# #     PAGE = "page"                 # Page number (for PDFs)

# class MetadataKeys:
#     FILENAME = "filename"
#     SECTION = "section"
#     LINE_NUMBER = "line_number"
#     SOURCE = "source" 

# class Endpoints:
#     """API Endpoints used in FastAPI app."""
#     ROOT = "/"
#     DATA = "/data"
#     DATA_BY_ID = "/data/{doc_id}"
#     RAW_DATA = "/raw_data"
#     UPLOAD_TEXT_FILE = "/upload-text-file"
#     UPLOAD_FILE = "/upload"              # New: Generic file upload (txt, pdf, docx)
#     SYNC_FILE = "/sync"                  # New: Force sync file with Chroma
#     ASK_RAG = "/ask_rag"                 # New: Ask RAG with query
#     ASK_RAG1 = "/ask_rag1"               # Optional second query route
#     LIST_COLLECTIONS = "/list_collections"
#     DELETE_COLLECTION = "/delete_collection"
#     DROP_DATABASE = "/drop-database"
#     RESET_DATABASE = "/reset_database"



from enum import Enum

class Endpoints(str, Enum):
    API_PREFIX = "/api"
    DATA = "/data"
    RAW_DATA = "/data/raw"
    DATA_BY_ID = "/data/{doc_id}"
    UPLOAD_TEXT_FILE = "/data/upload/text"
    DROP_DATABASE = "/data/drop"
    ASK_GEMINI = "/ask-gemini"
    ASK_RAG = "/ask-rag"
    ROOT = "/"

class Messages(str, Enum):
    # ChromaDB messages
    CHROMA_COLLECTION_CREATED = "ChromaDB collection created."
    CHROMA_COLLECTION_RETRIEVED = "ChromaDB collection retrieved."
    COLLECTION_EXISTS_WITH_DATA = "Collection  already exists with documents."
    COLLECTION_EXISTS_EMPTY = "Collection exists but is empty. Loading default data."
    DOCUMENTS_ADDED = "Documents added to ChromaDB."
    ADDING_DOCUMENTS = "Adding documents to ChromaDB..."
    DATABASE_DROPPED = "ChromaDB database folder  deleted successfully."

    # File related messages
    FILE_UPLOADED = "File  uploaded and processed successfully."
    FILE_NOT_FOUND = "File not found at"
    INVALID_FILE_TYPE = "Invalid file type. Only .txt, .pdf, and .docx files are allowed."
    NO_DATA_TO_PROCESS = "No data found in the file to process."

    # Document management messages
    DOC_NOT_FOUND = "Document not found."
    DOC_DELETED = "Document with ID deleted successfully."
    ALL_DOCS_DELETED = "All documents deleted successfully."
    DELETE_FAILED = "Failed to delete all documents."

    # Error messages
    ERROR_GENERAL = "An error occurred: {error}"
    ERROR_FILE_UPLOAD = "File upload failed: {error}"
    ERROR_DELETION = "Document deletion failed: {error}"
    DATABASE_NOT_FOUND = "Database directory not found at '{db_directory}'."

    # General messages
    APP_RUNNING = "Application is running"

class ChromaDBConfig(str, Enum):
    DB_DIRECTORY = "db_data"
    COLLECTION_NAME = "rag_collection"
    EMBEDDING_MODEL = "all-MiniLM-L6-v2"
    FILE_PATH = "data/source_docs.txt"

class MetadataKeys(str, Enum):
    SOURCE = "source"
    CHUNK_ID = "chunk_id"
    FILENAME = "filename"
    LINE_NUMBER = "line_number"
