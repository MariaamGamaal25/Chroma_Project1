# main.py
import os
import chromadb
from chromadb.utils import embedding_functions
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Any

# Initialize the FastAPI application
app = FastAPI()

# --- Pydantic Model for API Response ---
# This model defines the structure of the data we'll return from our API.
class Document(BaseModel):
    id: str
    text: str
    metadata: dict

# --- ChromaDB Configuration and Setup ---
# This function centralizes the logic for connecting to our ChromaDB collection.
def get_chroma_collection():
    """
    Initializes the ChromaDB client and connects to the 'text_data' collection
    within the 'trial_db' persistent directory.
    """
    # The directory where ChromaDB will store its data.
    persist_dir = os.path.join(os.getcwd(), "trial_db")

    # Create a persistent client. Data will be saved in the `persist_dir`.
    client = chromadb.PersistentClient(path=persist_dir)

    # Define the embedding function we'll use.
    embedding_func = embedding_functions.SentenceTransformerEmbeddingFunction(
        model_name="all-MiniLM-L6-v2"
    )

    # Get or create the collection.
    # The collection name is 'text_data', which is what you defined in your script.
    collection = client.get_or_create_collection(
        name="text_data",
        embedding_function=embedding_func
    )

    return collection

def store_text_file_once(collection, file_path: str):
    """
    Stores a text file into the ChromaDB collection, but only if the collection
    is currently empty. This prevents data duplication on reloads.
    """
    # Create a dummy file if one doesn't exist
    if not os.path.exists(file_path):
        print(f"File '{file_path}' not found. Creating a dummy file.")
        with open(file_path, "w", encoding="utf-8") as f:
            f.write("This is a sample document for ChromaDB.\n")
            f.write("The second line contains different text.\n")
            f.write("And this is the final line of our sample data.\n")

    # Read the file's content
    with open(file_path, "r", encoding="utf-8") as f:
        lines = [line.strip() for line in f if line.strip()]

    # Check if the collection already has documents.
    if collection.count() == 0:
        print("Collection is empty. Adding new documents...")
        ids = [f"line_{i}" for i in range(len(lines))]
        metadatas = [{"line_number": i, "source": file_path} for i in range(len(lines))]
        
        # Add the documents to the collection
        collection.add(
            documents=lines,
            ids=ids,
            metadatas=metadatas
        )
        print("Documents successfully added to the collection.")
    else:
        print("Collection already contains data. Skipping insertion.")

# --- FastAPI Endpoints ---

@app.get("/")
def read_root():
    """
    A simple root endpoint to check if the server is running.
    """
    return {"message": "ChromaDB FastAPI app is running!"}

@app.get("/data", response_model=list[Document])
def get_all_data():
    """
    Retrieves all documents from the ChromaDB collection in a structured format.
    """
    try:
        collection = get_chroma_collection()
        
        # Fetch all documents from the collection.
        results = collection.get(
            ids=None,
            include=['documents', 'metadatas']
        )

        # Format the results into a list of Document objects.
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
        print(f"An error occurred: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/data/{doc_id}", response_model=Document)
def get_document_by_id(doc_id: str):
    """
    Retrieves a single document by its ID from the ChromaDB collection.
    
    Args:
        doc_id: The ID of the document to retrieve (e.g., 'line_0').
    """
    try:
        collection = get_chroma_collection()
        
        # Fetch the specific document by its ID.
        results = collection.get(
            ids=[doc_id],
            include=['documents', 'metadatas']
        )

        # Check if the document was found.
        if not results.get('ids'):
            raise HTTPException(status_code=404, detail="Document not found")
        
        # Extract the single document and format it.
        doc = Document(
            id=results['ids'][0],
            text=results['documents'][0],
            metadata=results['metadatas'][0]
        )
        
        return doc
    except HTTPException as e:
        # Re-raise the HTTPException for FastAPI to handle
        raise e
    except Exception as e:
        print(f"An error occurred: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/raw_data")
def get_raw_data() -> dict[str, Any]:
    """
    Retrieves all documents from the ChromaDB collection and returns them in a raw
    dictionary format, mimicking the output of a ChromaDB query.
    """
    try:
        collection = get_chroma_collection()
        
        # Fetch all documents from the collection.
        results = collection.get(
            ids=None,
            include=['documents', 'metadatas']
        )

        # Format the results into the requested dictionary structure.
        # Note: A `get` operation does not have a `distances` key.
        # We are wrapping the list of documents and ids in an extra list to match
        # the format you provided.
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
        print(f"An error occurred: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    
@app.delete("/data/{doc_id}")  #replace doc_id with actual doc_id (ex.line_6)

#curl -X DELETE http://127.0.0.1:8000/data/line_6

def delete_document_by_id(doc_id: str):
    """
    Deletes a single document by its ID from the ChromaDB collection.

    Args:
        doc_id: The ID of the document to delete (e.g., 'line_0').
    """
    try:
        collection = get_chroma_collection()
        
        # Check if the document exists before attempting to delete.
        if collection.get(ids=[doc_id])['ids']:
            collection.delete(ids=[doc_id])
            return {"message": f"Document with ID '{doc_id}' deleted successfully."}
        else:
            raise HTTPException(status_code=404, detail="Document not found")
            
    except HTTPException as e:
        raise e
    except Exception as e:
        print(f"An error occurred during deletion: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/data")
def delete_all_data():
    """
    Deletes all documents from the ChromaDB collection.
    """
    try:
        collection = get_chroma_collection()
        count_before_delete = collection.count()
        collection.delete(ids=None, where={}) # Deletes all documents
        count_after_delete = collection.count()

        if count_after_delete == 0:
            return {"message": f"Successfully deleted all {count_before_delete} documents."}
        else:
            raise HTTPException(status_code=500, detail="Failed to delete all documents.")

    except Exception as e:
        print(f"An error occurred during bulk deletion: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# --- Main entry point for running the server ---
if __name__ == "__main__":
    import uvicorn
    
    # Pre-populate the database before starting the server.
    collection = get_chroma_collection()
    store_text_file_once(collection, "data_file.txt")
    
    # Run the FastAPI application with Uvicorn.
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
