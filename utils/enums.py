# utils/enums.py
class ChromaDBConfig:
    COLLECTION_NAME = "text_data"
    DB_DIRECTORY = "RAG_db"
    EMBEDDING_MODEL = "all-MiniLM-L6-v2"
    FILE_PATH = "raw_data\data_file.txt"

class Messages:
    APP_RUNNING = "ChromaDB FastAPI app is running!"
    DOC_NOT_FOUND = "Document not found"
    DOC_DELETED = "Document deleted successfully."
    ALL_DOCS_DELETED = "Successfully deleted all documents."
    DELETE_FAILED = "Failed to delete all documents."
    FILE_NOT_FOUND = "File not found."
    COLLECTION_EMPTY = "Collection is empty. Adding new documents..."
    DOCS_ADDED = "Documents successfully added to the collection."
    COLLECTION_NOT_EMPTY = "Collection already contains data. Skipping initialization."
    COLLECTION_EXISTS_WITH_DATA = "Collection already exists with documents. Skipping initialization."
    COLLECTION_EXISTS_EMPTY = "Collection  exists but is empty. Populating with data."
    COLLECTION_NOT_EXISTS = "Collection '{collection_name}' does not exist. Creating and populating with data."
    OPENING_FILE = "Opening file: {file_path}"
    READ_LINES = "Read non-empty lines from the file."
    ADDING_DOCUMENTS = "Adding documents to the collection..."
    DOCUMENTS_ADDED = "Documents added to the collection."
    FORCE_CLEAR_COLLECTION = "Force mode enabled. Clearing collection."
    FILE_UPLOADED = "File successfully processed and stored in collection."
    INVALID_FILE_TYPE = "Only .txt files are supported."
    ERROR_GENERAL = "An error occurred"
    ERROR_DELETION = "An error occurred during deletion"
    ERROR_FILE_UPLOAD = "An error occurred during file upload"
    DATABASE_DROPPED = "Database directory  successfully deleted."
    DATABASE_NOT_FOUND = "Database directory  does not exist."

class MetadataKeys:
    LINE_NUMBER = "line_number"
    SOURCE = "source"

class Endpoints:
    ROOT = "/"
    DATA = "/data"
    DATA_BY_ID = "/data/{doc_id}"
    RAW_DATA = "/raw_data"
    UPLOAD_TEXT_FILE = "/upload-text-file"
    DROP_DATABASE = "/drop-database"