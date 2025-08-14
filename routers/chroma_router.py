
from fastapi import APIRouter, HTTPException, UploadFile, File
from typing import Any
from dtos.document import Document
from utils.enums import Endpoints, Messages, ChromaDBConfig
from chroma_functionalities import get_chroma_collection, sync_text_file_with_collection
import os
import shutil
from utils.logger import setup_logger
from gemini_client import ask_gemini

# Initialize logger
logger = setup_logger(__name__)

# Initialize the router
router = APIRouter()


@router.get(Endpoints.DATA, response_model=list[Document])
def get_all_data():
    """Retrieve all documents from the ChromaDB collection."""
    try:
        collection = get_chroma_collection()
        results = collection.get(ids=None, include=['documents', 'metadatas'])
        all_documents = [
            Document(id=results['ids'][i],
                     text=results['documents'][i],
                     metadata=results['metadatas'][i])
            for i in range(len(results.get('ids', [])))
        ]
        return all_documents
    except Exception as e:
        logger.error(Messages.ERROR_GENERAL.format(error=str(e)))
        raise HTTPException(status_code=500, detail=str(e))


@router.get(Endpoints.DATA_BY_ID, response_model=Document)
def get_document_by_id(doc_id: str):
    """Retrieve a single document by ID."""
    try:
        collection = get_chroma_collection()
        results = collection.get(ids=[doc_id], include=['documents', 'metadatas'])
        if not results.get('ids'):
            raise HTTPException(status_code=404, detail=Messages.DOC_NOT_FOUND)
        return Document(
            id=results['ids'][0],
            text=results['documents'][0],
            metadata=results['metadatas'][0]
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(Messages.ERROR_GENERAL.format(error=str(e)))
        raise HTTPException(status_code=500, detail=str(e))


@router.get(Endpoints.RAW_DATA)
def get_raw_data() -> dict[str, Any]:
    """Retrieve all documents from ChromaDB in raw format."""
    try:
        collection = get_chroma_collection()
        results = collection.get(ids=None, include=['documents', 'metadatas'])
        return {
            'documents': [results.get('documents', [])],
            'ids': [results.get('ids', [])],
            'distances': None,
            'uris': None,
            'data': None,
            'metadatas': [results.get('metadatas', [])],
            'embeddings': None
        }
    except Exception as e:
        logger.error(Messages.ERROR_GENERAL.format(error=str(e)))
        raise HTTPException(status_code=500, detail=str(e))


@router.delete(Endpoints.DATA_BY_ID)
def delete_document_by_id(doc_id: str):
    """Delete a document by ID."""
    try:
        collection = get_chroma_collection()
        if collection.get(ids=[doc_id])['ids']:
            collection.delete(ids=[doc_id])
            return {"message": Messages.DOC_DELETED.format(doc_id=doc_id)}
        else:
            raise HTTPException(status_code=404, detail=Messages.DOC_NOT_FOUND)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(Messages.ERROR_DELETION.format(error=str(e)))
        raise HTTPException(status_code=500, detail=str(e))


@router.delete(Endpoints.DATA)
def delete_all_data():
    """Delete all documents from ChromaDB."""
    try:
        collection = get_chroma_collection()
        count_before_delete = collection.count()

        if count_before_delete == 0:
            return {"message": "No documents to delete"}

        ids = collection.get(include=[], ids=None)['ids']
        if ids:
            collection.delete(ids=ids)

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
    """Upload a text file and store its contents in ChromaDB."""
    try:
        if not file.filename.endswith('.txt'):
            raise HTTPException(status_code=400, detail=Messages.INVALID_FILE_TYPE)

        temp_file_path = f"temp_{file.filename}"
        with open(temp_file_path, "wb") as temp_file:
            content = await file.read()
            temp_file.write(content)

        try:
            collection = get_chroma_collection()

            if force:
                logger.info(f"Force clearing collection '{ChromaDBConfig.COLLECTION_NAME}' before upload")
                ids = collection.get(include=[], ids=None)['ids']
                if ids:
                    collection.delete(ids=ids)

            sync_text_file_with_collection(collection, temp_file_path, force=False)
            return {"message": Messages.FILE_UPLOADED.format(file_name=file.filename)}

        finally:
            if os.path.exists(temp_file_path):
                os.remove(temp_file_path)

    except FileNotFoundError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(Messages.ERROR_FILE_UPLOAD.format(error=str(e)))
        raise HTTPException(status_code=500, detail=str(e))


@router.delete(Endpoints.DROP_DATABASE)
def drop_database():
    """Delete the entire ChromaDB database folder."""
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



