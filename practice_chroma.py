import os
import chromadb
from chromadb.utils import embedding_functions

def store_text_file(collection, file_path: str):
    print(f"Opening file: {file_path}")
    with open(file_path, encoding="utf-8") as f:
        lines = [line.strip() for line in f if line.strip()]
    print(f"Read {len(lines)} non-empty lines from the file.")

    ids = [f"line_{i}" for i in range(len(lines))]
    metadatas = [{"line_number": i, "source": file_path} for i in range(len(lines))]

    print("Adding documents to the collection...")
    collection.add(
        documents=lines,
        ids=ids,
        metadatas=metadatas
    )
    print("Documents added to the collection.")

def main():
    print("Setting up embedding function...")
    embedding_func = embedding_functions.SentenceTransformerEmbeddingFunction(
        model_name="all-MiniLM-L6-v2"
    )
    print("Embedding function set up.")

    # Create a persistent client that saves data to a local directory
    # The default path is "./chroma", but we're being explicit here.
    persist_dir = os.path.join(os.getcwd(), "trial_db")
    client = chromadb.PersistentClient(path=persist_dir)
    print(f"Chroma persistent client created. Data will be saved to: {persist_dir}")

    print("Getting or creating collection with embedding function...")
    collection = client.get_or_create_collection(
        name="text_data",
        embedding_function=embedding_func
    )
    print("Collection ready.")

    file_path = r"data_file.txt"
    print(f"Starting to store text from {file_path}...")
    store_text_file(collection, file_path)
    print("Finished storing text.")

    print("All done. The database is now persisted on disk.")

if __name__ == "__main__":
    main()