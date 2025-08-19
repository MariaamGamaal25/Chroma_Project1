# Project Documentation

This project for a Retrieval-Augmented Generation (RAG) system. It features a FastAPI application that utilizes ChromaDB as a vector database to manage and retrieve documents. The current implementation provides a REST API for interacting with the documents.

# Project Files
- chroma_operations.py: This is the main application file. It initializes a FastAPI app, sets up a persistent ChromaDB client, and defines the API endpoints. It also includes a function to pre-populate the database with a text file on the first run.

- practice_chroma.py: A standalone Python script that showcases how to use the ChromaDB client and its add functionality to store data from a text file. This file is for demonstration purposes and is not part of the FastAPI application's runtime.

- data_file.txt: A simple text file that contains the data to be loaded into the ChromaDB collection. Each line in this file is treated as a separate document.

- requirements.txt: This file lists all the Python dependencies required to run the project, including fastapi, chromadb, and uvicorn.

- .gitignore: A file for version control systems (like Git) that specifies which files and directories should be ignored and not tracked.

# Project Flow
The project is structured to be easy to run and test. The overall flow is as follows:

- Dependencies are installed using the requirements.txt file.

- The main application (chroma_operations.py) is started with a server like Uvicorn.

- On startup, the sync_text_file_with_collection function is called. This function checks if the ChromaDB collection is empty.

- If the collection is empty, it reads the content of data_file.txt, splits it into lines, and adds each line as a document to the ChromaDB collection.

- If the collection already contains data, the script skips the data insertion step to prevent duplication.

- The FastAPI server then becomes active, and you can interact with the data through the defined API endpoints.

# How to Run the Project
Follow these steps to set up and run the project locally.

# Step 1: Clone the Repository (if applicable) and Navigate to the Project Directory
First, ensure you are in the directory containing the project files.

# If you are using Git, you would clone the repository
git clone <repository_url>
cd <project_directory>



# Step 2: Create and Activate a Virtual Environment (Recommended)
Using a virtual environment is a best practice to manage project dependencies.

# Create a virtual environment named 'venv'
python -m venv venv

# Activate the virtual environment
# On macOS and Linux:
source venv/bin/activate
# On Windows:
venv\Scripts\activate



# Step 3: Install Dependencies
Once the virtual environment is active, install all the required packages from requirements.txt.

pip install -r requirements.txt



# Step 4 (Optional): Pre-populate the Database with practice_chroma.py
You can run the practice_chroma.py script to manually populate the database before starting the FastAPI server. This is useful for testing or if you prefer to seed the database separately.

python practice_chroma.py



# Step 5: Run the Application
Start the FastAPI application using Uvicorn. The --reload flag is useful for development as it automatically restarts the server when code changes are detected.

uvicorn chroma_operations:app --reload



# Step 6: Access the API
The application will now be running on your local machine. You can access the API at http://127.0.0.1:8000.

To view the interactive API documentation and test the endpoints, open your web browser and navigate to:

# To show all documents 
http://127.0.0.1:8000/data to show all data

# Example: To show specific document with the ID 'line_6'
http://127.0.0.1:8000/data/line_6 

API DELETE Endpoints
Once the FastAPI server is running, you can use these DELETE endpoints to remove data from the ChromaDB collection.

Delete a single document by ID:
To delete a single document, you need to provide its unique ID. Based on your practice_chroma.py file, the IDs are formatted as line_0, line_1, etc.

# Example: Delete the document with the ID 'line_0'
curl -X DELETE "http://127.0.0.1:8000/data/line_0"

Delete all documents:
To clear the entire collection, you can use the bulk delete endpoint.

# This command deletes all documents in the collection
curl -X DELETE "http://127.0.0.1:8000/data"

Commands Explained
python -m venv venv: Creates a new virtual environment named venv in the current directory.

source venv/bin/activate: Activates the virtual environment on Unix-like systems (Linux/macOS). This command modifies your shell's environment to use the Python interpreter and packages from the venv directory.

venv\Scripts\activate: Activates the virtual environment on Windows.

pip install -r requirements.txt: Reads the requirements.txt file and installs all the listed Python packages and their specified versions.

python practice_chroma.py: Executes the practice_chroma.py script, which will create the ChromaDB collection and store the documents from data_file.txt.

uvicorn chroma_operations:app --reload: This is the command to run the application server.

uvicorn: The command to start the Uvicorn server.

chroma_operations:app: This specifies the entry point for the application. chroma_operations is the Python module (file name without .py), and app is the FastAPI application instance defined within that module.

--reload: A flag that tells Uvicorn to watch for changes in your code and automatically restart the server when a file is modified. This is great for development.
