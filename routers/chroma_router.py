from fastapi import APIRouter, HTTPException, UploadFile, File
from typing import Any
from dtos.document import Document
from utils.enums import Endpoints, Messages, ChromaDBConfig
from chroma_functionalities import get_chroma_collection, store_text_file_once
import os
import shutil
from utils.logger import setup_logger

# Initialize logger
logger = setup_logger(__name__)

# Initialize the router
router = APIRouter()

@router.get(Endpoints.DATA, response_model=list[Document])
def get_all_data():
    """
    Retrieves all documents from the ChromaDB collection in a structured format.
    """
    try:
        collection = get_chroma_collection()
        results = collection.get(
            ids=None,
            include=['documents', 'metadatas']
        )
        all_documents = []
        if results.get('ids'):
            for i in range(len(results['ids'])):
                doc = Document(
                    id=results['ids'][i],
                    text=results['documents'][i],
                    metadata=results['metadatas'][i]
                )
                all_documents.append(doc)
        return all_documents
    except Exception as e:
        logger.error(Messages.ERROR_GENERAL.format(error=str(e)))
        raise HTTPException(status_code=500, detail=str(e))

@router.get(Endpoints.DATA_BY_ID, response_model=Document)
def get_document_by_id(doc_id: str):
    """
    Retrieves a single document by its ID from the ChromaDB collection.
    
    Args:
        doc_id: The ID of the document to retrieve (e.g., a UUID4 string).
    """
    try:
        collection = get_chroma_collection()
        results = collection.get(
            ids=[doc_id],
            include=['documents', 'metadatas']
        )
        if not results.get('ids'):
            raise HTTPException(status_code=404, detail=Messages.DOC_NOT_FOUND)
        doc = Document(
            id=results['ids'][0],
            text=results['documents'][0],
            metadata=results['metadatas'][0]
        )
        return doc
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(Messages.ERROR_GENERAL.format(error=str(e)))
        raise HTTPException(status_code=500, detail=str(e))

@router.get(Endpoints.RAW_DATA)
def get_raw_data() -> dict[str, Any]:
    """
    Retrieves all documents from the ChromaDB collection and returns them in a raw
    dictionary format, mimicking the output of a ChromaDB query.
    """
    try:
        collection = get_chroma_collection()
        results = collection.get(
            ids=None,
            include=['documents', 'metadatas']
        )
        raw_output = {
            'documents': [results.get('documents', [])],
            'ids': [results.get('ids', [])],
            'distances': None,
            'uris': None,
            'data': None,
            'metadatas': [results.get('metadatas', [])],
            'embeddings': None
        }
        return raw_output
    except Exception as e:
        logger.error(Messages.ERROR_GENERAL.format(error=str(e)))
        raise HTTPException(status_code=500, detail=str(e))

@router.delete(Endpoints.DATA_BY_ID)
def delete_document_by_id(doc_id: str):
    """
    Deletes a single document by its ID from the ChromaDB collection.

    Args:
        doc_id: The ID of the document to delete (e.g., a UUID4 string).
    """
    try:
        collection = get_chroma_collection()
        if collection.get(ids=[doc_id])['ids']:
            collection.delete(ids=[doc_id])
            return {"message": Messages.DOC_DELETED.format(doc_id=doc_id)}
        else:
            raise HTTPException(status_code=404, detail=Messages.DOC_NOT_FOUND)
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(Messages.ERROR_DELETION.format(error=str(e)))
        raise HTTPException(status_code=500, detail=str(e))

@router.delete(Endpoints.DATA)
def delete_all_data():
    """
    Deletes all documents from the ChromaDB collection.
    """
    try:
        collection = get_chroma_collection()
        count_before_delete = collection.count()
        collection.delete(ids=None, where={})
        count_after_delete = collection.count()
        if count_after_delete == 0:
            return {"message": Messages.ALL_DOCS_DELETED.format(count_before_delete=count_before_delete)}
        else:
            raise HTTPException(status_code=500, detail=Messages.DELETE_FAILED)
    except Exception as e:
        logger.error(Messages.ERROR_DELETION.format(error=str(e)))
        raise HTTPException(status_code=500, detail=str(e))

@router.post(Endpoints.UPLOAD_TEXT_FILE)
async def upload_text_file(file: UploadFile = File(...), force: bool = False):
    """
    Uploads a text file and stores its contents as embeddings in the ChromaDB collection.
    
    Args:
        file: The uploaded text file.
        force: If True, clears the collection before storing the new file's contents.
        
    Returns:
        A message indicating the result of the operation.
        
    Raises:
        HTTPException: If the file is not a text file or cannot be processed.
    """
    try:
        # Validate file extension
        if not file.filename.endswith('.txt'):
            raise HTTPException(status_code=400, detail=Messages.INVALID_FILE_TYPE)
        
        # Save the uploaded file temporarily
        temp_file_path = f"temp_{file.filename}"
        with open(temp_file_path, "wb") as temp_file:
            content = await file.read()
            temp_file.write(content)
        
        try:
            # Process the file and store in ChromaDB
            collection = get_chroma_collection()
            store_text_file_once(collection, temp_file_path, force=force)
            return {"message": Messages.FILE_UPLOADED.format(file_name=file.filename)}
        finally:
            # Clean up the temporary file
            if os.path.exists(temp_file_path):
                os.remove(temp_file_path)
                
    except FileNotFoundError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(Messages.ERROR_FILE_UPLOAD.format(error=str(e)))
        raise HTTPException(status_code=500, detail=str(e))

@router.delete(Endpoints.DROP_DATABASE)
def drop_database():
    """
    Deletes the entire ChromaDB database by removing the 'RAG_db' directory.
    
    Returns:
        A message indicating the result of the operation.
        
    Raises:
        HTTPException: If the database directory cannot be deleted.
    """
    try:
        db_directory = os.path.join(os.getcwd(), ChromaDBConfig.DB_DIRECTORY)
        if os.path.exists(db_directory):
            shutil.rmtree(db_directory)
            return {"message": Messages.DATABASE_DROPPED.format(db_directory=db_directory)}
        else:
            raise HTTPException(status_code=404, detail=Messages.DATABASE_NOT_FOUND.format(db_directory=db_directory))
    except Exception as e:
        logger.error(Messages.ERROR_GENERAL.format(error=str(e)))
        raise HTTPException(status_code=500, detail=str(e))