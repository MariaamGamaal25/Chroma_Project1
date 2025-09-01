# # routers/chroma_router.py
# import os
# import shutil
# import tempfile
# from typing import Any

# from fastapi import APIRouter, HTTPException, UploadFile, File

# from dtos.document import Document
# from utils.enums import Endpoints, Messages, ChromaDBConfig, MetadataKeys
# from utils.logger import setup_logger
# from chroma_functionalities import get_chroma_collection, sync_text_file_with_collection

# logger = setup_logger(__name__)
# router = APIRouter()

# @router.get(Endpoints.DATA, response_model=list[Document], tags=["Data Management"])
# def get_all_data():
#     try:
#         collection = get_chroma_collection()
#         results = collection.get(ids=None, include=["documents", "metadatas"])
#         ids = results.get("ids", [])
#         return [
#             Document(
#                 id=ids[i],
#                 text=results["documents"][i],
#                 metadata=results["metadatas"][i]
#             )
#             for i in range(len(ids))
#         ]
#     except Exception as e:
#         logger.error(Messages.ERROR_GENERAL.value.format(error=str(e)))
#         raise HTTPException(status_code=500, detail=str(e))

# @router.get(Endpoints.DATA_BY_ID, response_model=Document, tags=["Data Management"])
# def get_document_by_id(doc_id: str):
#     try:
#         collection = get_chroma_collection()
#         results = collection.get(ids=[doc_id], include=["documents", "metadatas"])
#         if not results.get("ids"):
#             raise HTTPException(status_code=404, detail=Messages.DOC_NOT_FOUND.value)
#         return Document(
#             id=results["ids"][0],
#             text=results["documents"][0],
#             metadata=results["metadatas"][0]
#         )
#     except HTTPException:
#         raise
#     except Exception as e:
#         logger.error(Messages.ERROR_GENERAL.value.format(error=str(e)))
#         raise HTTPException(status_code=500, detail=str(e))

# @router.get(Endpoints.RAW_DATA, tags=["Data Management"])
# def get_raw_data() -> dict[str, Any]:
#     try:
#         collection = get_chroma_collection()
#         results = collection.get(ids=None, include=["documents", "metadatas"])
#         return {
#             "documents": results.get("documents", []),
#             "ids": results.get("ids", []),
#             "metadatas": results.get("metadatas", []),
#             "embeddings": None,
#             "distances": None,
#             "uris": None,
#             "data": None,
#         }
#     except Exception as e:
#         logger.error(Messages.ERROR_GENERAL.value.format(error=str(e)))
#         raise HTTPException(status_code=500, detail=str(e))

# @router.delete(Endpoints.DATA_BY_ID, tags=["Data Management"])
# def delete_document_by_id(doc_id: str):
#     try:
#         collection = get_chroma_collection()
#         results = collection.get(ids=[doc_id])
#         if not results["ids"]:
#             raise HTTPException(status_code=404, detail=Messages.DOC_NOT_FOUND.value)
#         collection.delete(ids=[doc_id])
#         return {"message": Messages.DOC_DELETED.value.replace("deleted", f"{doc_id} deleted")}
#     except HTTPException:
#         raise
#     except Exception as e:
#         logger.error(Messages.ERROR_DELETION.value.format(error=str(e)))
#         raise HTTPException(status_code=500, detail=str(e))

# @router.delete(Endpoints.DATA, tags=["Data Management"])
# def delete_all_data():
#     try:
#         collection = get_chroma_collection()
#         ids = collection.get(ids=None, include=[])["ids"]
#         if not ids:
#             return {"message": "No documents to delete"}
#         collection.delete(ids=ids)
#         return {"message": Messages.ALL_DOCS_DELETED.value}
#     except Exception as e:
#         logger.error(Messages.ERROR_DELETION.value.format(error=str(e)))
#         raise HTTPException(status_code=500, detail=str(e))

# @router.post(Endpoints.UPLOAD_TEXT_FILE, tags=["Sync Data to chroma"])
# async def upload_text_file(file: UploadFile = File(...), force: bool = False):
#     """
#     Upload .txt / .pdf / .docx and index to ChromaDB.
#     For PDFs, OCR (Arabic+English) is applied automatically when needed.
#     """
#     try:
#         ext = os.path.splitext(file.filename)[1].lower()
#         if ext not in (".txt", ".pdf", ".docx"):
#             raise HTTPException(status_code=400, detail=Messages.INVALID_FILE_TYPE.value)

#         with tempfile.TemporaryDirectory() as temp_dir:
#             temp_path = os.path.join(temp_dir, file.filename)
#             with open(temp_path, "wb") as out:
#                 shutil.copyfileobj(file.file, out)

#             collection = get_chroma_collection()
#             sync_text_file_with_collection(collection, temp_path, force=force)

#         return {"message": Messages.FILE_UPLOADED.value.replace("File ", f"File '{file.filename}' ")}
#     except FileNotFoundError as e:
#         raise HTTPException(status_code=400, detail=str(e))
#     except Exception as e:
#         logger.error(Messages.ERROR_FILE_UPLOAD.value.format(error=str(e)))
#         raise HTTPException(status_code=500, detail=str(e))

# @router.delete(Endpoints.DROP_DATABASE, tags=["Data Management"])
# def drop_database():
#     try:
#         db_directory = os.path.abspath(ChromaDBConfig.DB_DIRECTORY.value)
#         if not os.path.exists(db_directory):
#             raise HTTPException(
#                 status_code=404,
#                 detail=Messages.DATABASE_NOT_FOUND.value.format(db_directory=db_directory)
#             )
#         shutil.rmtree(db_directory, ignore_errors=False)
#         logger.info(Messages.DATABASE_DROPPED.value.format(db_directory=db_directory))
#         return {"message": Messages.DATABASE_DROPPED.value.format(db_directory=db_directory)}
#     except Exception as e:
#         logger.error(Messages.ERROR_GENERAL.value.format(error=str(e)))
#         raise HTTPException(status_code=500, detail=str(e))

# @router.post("/upload-file", tags=["Sync Data to Chroma"])
# async def upload_file(file: UploadFile = File(...), force: bool = False):
#     """
#     Upload .txt / .pdf / .docx and index to ChromaDB.
#     - If PDF: extracts table rows.
#     - If text/docx: extracts paragraphs.
#     """
#     try:
#         ext = os.path.splitext(file.filename)[1].lower()
#         if ext not in (".txt", ".pdf", ".docx"):
#             raise HTTPException(status_code=400, detail=Messages.INVALID_FILE_TYPE.value)

#         with tempfile.TemporaryDirectory() as temp_dir:
#             temp_path = os.path.join(temp_dir, file.filename)
#             with open(temp_path, "wb") as out:
#                 shutil.copyfileobj(file.file, out)

#             collection = get_chroma_collection()
#             sync_text_file_with_collection(collection, temp_path, force=force)

#         return {"message": f"File '{file.filename}' processed and indexed."}
#     except FileNotFoundError as e:
#         raise HTTPException(status_code=400, detail=str(e))
#     except Exception as e:
#         logger.error(Messages.ERROR_FILE_UPLOAD.value.format(error=str(e)))
#         raise HTTPException(status_code=500, detail=str(e))

import os
import shutil
import tempfile
from typing import Any

from fastapi import APIRouter, HTTPException, UploadFile, File

from dtos.document import Document
from utils.enums import Endpoints, Messages, ChromaDBConfig, MetadataKeys
from utils.logger import setup_logger
from chroma_functionalities import get_chroma_collection, sync_text_file_with_collection

logger = setup_logger(__name__)
router = APIRouter(prefix=Endpoints.API_PREFIX.value, tags=["Data Management"])

# ---------- CRUD Endpoints ----------
@router.get(Endpoints.DATA.value, response_model=list[Document])
def get_all_data():
    try:
        collection = get_chroma_collection()
        results = collection.get(ids=None, include=["documents", "metadatas"])
        ids = results.get("ids", [])
        return [
            Document(
                id=ids[i],
                text=results["documents"][i],
                metadata=results["metadatas"][i]
            )
            for i in range(len(ids))
        ]
    except Exception as e:
        logger.error(Messages.ERROR_GENERAL.value.format(error=str(e)))
        raise HTTPException(status_code=500, detail=str(e))


@router.get(Endpoints.DATA_BY_ID.value, response_model=Document)
def get_document_by_id(doc_id: str):
    try:
        collection = get_chroma_collection()
        results = collection.get(ids=[doc_id], include=["documents", "metadatas"])
        if not results.get("ids"):
            raise HTTPException(status_code=404, detail=Messages.DOC_NOT_FOUND.value)
        return Document(
            id=results["ids"][0],
            text=results["documents"][0],
            metadata=results["metadatas"][0]
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(Messages.ERROR_GENERAL.value.format(error=str(e)))
        raise HTTPException(status_code=500, detail=str(e))


@router.get(Endpoints.RAW_DATA.value)
def get_raw_data() -> dict[str, Any]:
    try:
        collection = get_chroma_collection()
        results = collection.get(ids=None, include=["documents", "metadatas"])
        return {
            "documents": results.get("documents", []),
            "ids": results.get("ids", []),
            "metadatas": results.get("metadatas", []),
        }
    except Exception as e:
        logger.error(Messages.ERROR_GENERAL.value.format(error=str(e)))
        raise HTTPException(status_code=500, detail=str(e))


@router.delete(Endpoints.DATA_BY_ID.value)
def delete_document_by_id(doc_id: str):
    try:
        collection = get_chroma_collection()
        results = collection.get(ids=[doc_id])
        if not results["ids"]:
            raise HTTPException(status_code=404, detail=Messages.DOC_NOT_FOUND.value)
        collection.delete(ids=[doc_id])
        return {"message": Messages.DOC_DELETED.value}
    except Exception as e:
        logger.error(Messages.ERROR_DELETION.value.format(error=str(e)))
        raise HTTPException(status_code=500, detail=str(e))


# @router.delete(Endpoints.DATA.value)
# def delete_all_data():
#     try:
#         db_path = ChromaDBConfig.DB_DIRECTORY.value
#         if os.path.exists(db_path):
#             shutil.rmtree(db_path)
#             return {"message": Messages.ALL_DOCS_DELETED.value}
#         else:
#             return {"message": Messages.DATABASE_NOT_FOUND.value.format(db_directory=db_path)}
#     except Exception as e:
#         logger.error(Messages.ERROR_DELETION.value.format(error=str(e)))
#         raise HTTPException(status_code=500, detail=str(e))


@router.post(Endpoints.UPLOAD_TEXT_FILE.value, tags=["Sync Data to chroma"])
async def upload_text_file(file: UploadFile = File(...), force: bool = False):
    try:
        ext = os.path.splitext(file.filename)[1].lower()
        if ext not in (".txt", ".pdf", ".docx"):
            raise HTTPException(status_code=400, detail=Messages.INVALID_FILE_TYPE.value)

        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = os.path.join(temp_dir, file.filename)
            with open(temp_path, "wb") as out:
                shutil.copyfileobj(file.file, out)

            collection = get_chroma_collection()
            sync_text_file_with_collection(collection, temp_path, force=force)

        return {"message": Messages.FILE_UPLOADED.value}
    except FileNotFoundError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(Messages.ERROR_FILE_UPLOAD.value.format(error=str(e)))
        raise HTTPException(status_code=500, detail=str(e))


@router.delete(Endpoints.DROP_DATABASE.value)
def drop_database():
    try:
        db_directory = os.path.abspath(ChromaDBConfig.DB_DIRECTORY.value)
        if not os.path.exists(db_directory):
            raise HTTPException(
                status_code=404,
                detail=Messages.DATABASE_NOT_FOUND.value.format(db_directory=db_directory)
            )
        shutil.rmtree(db_directory, ignore_errors=False)
        logger.info(Messages.DATABASE_DROPPED.value.format(db_directory=db_directory))
        return {"message": Messages.DATABASE_DROPPED.value.format(db_directory=db_directory)}
    except Exception as e:
        logger.error(Messages.ERROR_GENERAL.value.format(error=str(e)))
        raise HTTPException(status_code=500, detail=str(e))
    
    
@router.delete(Endpoints.DATA, tags=["Data Management"])
def delete_all_data():
    try:
        collection = get_chroma_collection()
        ids = collection.get(ids=None, include=[])["ids"]
        if not ids:
            return {"message": "No documents to delete"}
        collection.delete(ids=ids)
        return {"message": Messages.ALL_DOCS_DELETED.value}
    except Exception as e:
        logger.error(Messages.ERROR_DELETION.value.format(error=str(e)))
        raise HTTPException(status_code=500, detail=str(e))
