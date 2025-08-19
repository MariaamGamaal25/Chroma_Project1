# import streamlit as st
# import requests
# import os

# # --- Configuration ---
# FASTAPI_URL = "http://localhost:8000"  # Adjust this if your FastAPI server is on a different port or host.

# st.set_page_config(
#     page_title="RAG-Powered Chatbot",
#     page_icon="🤖",
#     layout="wide"
# )

# # --- UI Layout ---
# st.title("📄 RAG-Powered Document Q&A")
# st.markdown("Ask a question about the documents in the knowledge base. The system will retrieve the most relevant information and use it to generate an answer.")

# # --- File Upload & Admin Sidebar ---
# with st.sidebar:
#     st.header("Admin Panel")
#     st.markdown("Manage your documents and the ChromaDB database.")

#     # File Uploader
#     st.subheader("Upload Document")
#     uploaded_file = st.file_uploader(
#         "Upload a .txt file:",
#         type="txt",
#         accept_multiple_files=False,
#         help="The content of this file will be chunked and added to the knowledge base."
#     )
#     force_upload = st.checkbox("Force upload (delete existing chunks from this file)")

#     if st.button("Add Document"):
#         if uploaded_file is not None:
#             with st.spinner("Uploading and processing file..."):
#                 try:
#                     # Prepare file for upload
#                     files = {'file': (uploaded_file.name, uploaded_file.getvalue(), 'text/plain')}
#                     params = {'force': 'true'} if force_upload else {}
#                     response = requests.post(f"{FASTAPI_URL}/upload-text-file", files=files, params=params)

#                     if response.status_code == 200:
#                         st.success(f"File '{uploaded_file.name}' processed successfully!")
#                     else:
#                         st.error(f"Failed to upload file. Status: {response.status_code}, Detail: {response.text}")
#                 except Exception as e:
#                     st.error(f"An error occurred: {str(e)}")
#         else:
#             st.warning("Please upload a file first.")

#     st.markdown("---")
    
#     # Database Management Buttons
#     st.subheader("Database Actions")
#     col1, col2 = st.columns(2)
#     with col1:
#         if st.button("Delete All Documents", type="primary"):
#             if st.session_state.get('confirm_delete', False):
#                 with st.spinner("Deleting all documents..."):
#                     try:
#                         response = requests.delete(f"{FASTAPI_URL}/data")
#                         if response.status_code == 200:
#                             st.success("All documents deleted from the collection.")
#                             st.session_state['confirm_delete'] = False  # Reset confirmation
#                         else:
#                             st.error(f"Failed to delete documents: {response.text}")
#                     except Exception as e:
#                         st.error(f"An error occurred: {str(e)}")
#             else:
#                 st.warning("Click again to confirm deletion of all documents.")
#                 st.session_state['confirm_delete'] = True

#     with col2:
#         if st.button("Drop Entire Database", type="secondary"):
#             if st.session_state.get('confirm_drop', False):
#                 with st.spinner("Dropping the entire database..."):
#                     try:
#                         response = requests.delete(f"{FASTAPI_URL}/drop-database")
#                         if response.status_code == 200:
#                             st.success("Database directory successfully dropped. Restart the FastAPI server to reinitialize.")
#                             st.session_state['confirm_drop'] = False # Reset confirmation
#                         else:
#                             st.error(f"Failed to drop database: {response.text}")
#                     except Exception as e:
#                         st.error(f"An error occurred: {str(e)}")
#             else:
#                 st.warning("Click again to confirm dropping the entire database.")
#                 st.session_state['confirm_drop'] = True

# # --- Main Interface ---
# # User Query Input
# st.subheader("Ask a Question")
# query_text = st.text_area(
#     "Enter your question here:",
#     height=100,
#     placeholder="e.g., What is the policy for remote work?"
# )

# # Button to submit query
# if st.button("Get Answer", use_container_width=True, type="primary"):
#     if query_text:
#         with st.spinner("Searching and generating answer..."):
#             try:
#                 # Send a POST request to the FastAPI /ask_rag endpoint
#                 response = requests.post(f"{FASTAPI_URL}/ask_rag", json={"query": query_text})
                
#                 if response.status_code == 200:
#                     result = response.json()
#                     answer = result.get("answer")
#                     documents_used = result.get("documents_used", [])

#                     # Display the answer
#                     st.success("Answer:")
#                     st.write(answer)
                    
#                     # Display the source documents
#                     st.markdown("---")
#                     st.subheader("Sources Used:")
#                     for doc in documents_used:
#                         source = doc.get("metadata", {}).get("source", "Unknown Source")
#                         content = doc.get("doc", "No content available.")
#                         st.expander(f"**Source:** `{source}`").markdown(f"**Content:**\n{content}")
#                 else:
#                     st.error(f"An error occurred with the request. Status: {response.status_code}, Detail: {response.text}")
#             except requests.exceptions.ConnectionError:
#                 st.error("Connection error. Please ensure your FastAPI server is running.")
#             except Exception as e:
#                 st.error(f"An unexpected error occurred: {str(e)}")
#     else:
#         st.warning("Please enter a question to get an answer.")

# st.markdown("---")
# st.info("The application connects to a FastAPI backend running on `localhost:8000` to handle document management and RAG.")

# # Add a link to the FastAPI docs for convenience
# st.markdown("For API details, visit the [FastAPI documentation](http://localhost:8000/docs).")


import streamlit as st
import requests
import os

# --- Configuration ---
# Update the base URL to include the /api prefix
FASTAPI_URL = "http://localhost:8000/api"

st.set_page_config(
    page_title="RAG-Powered Chatbot",
    page_icon="🤖",
    layout="wide"
)

# --- UI Layout ---
st.title("📄 RAG-Powered Document Q&A")
st.markdown("Ask a question about the documents in the knowledge base. The system will retrieve the most relevant information and use it to generate an answer.")

# --- File Upload & Admin Sidebar ---
with st.sidebar:
    st.header("Admin Panel")
    st.markdown("Manage your documents and the ChromaDB database.")

    # File Uploader
    st.subheader("Upload Document")
    uploaded_file = st.file_uploader(
        "Upload a .txt file:",
        type="txt",
        accept_multiple_files=False,
        help="The content of this file will be chunked and added to the knowledge base."
    )
    force_upload = st.checkbox("Force upload (delete existing chunks from this file)")

    if st.button("Add Document"):
        if uploaded_file is not None:
            with st.spinner("Uploading and processing file..."):
                try:
                    # Prepare file for upload
                    files = {'file': (uploaded_file.name, uploaded_file.getvalue(), 'text/plain')}
                    params = {'force': 'true'} if force_upload else {}
                    # Corrected URL to include /api prefix
                    response = requests.post(f"{FASTAPI_URL}/upload-text-file", files=files, params=params)

                    if response.status_code == 200:
                        st.success(f"File '{uploaded_file.name}' processed successfully!")
                    else:
                        st.error(f"Failed to upload file. Status: {response.status_code}, Detail: {response.text}")
                except Exception as e:
                    st.error(f"An error occurred: {str(e)}")
        else:
            st.warning("Please upload a file first.")

    st.markdown("---")

    # Database Management Buttons
    st.subheader("Database Actions")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Delete All Documents", type="primary"):
            if st.session_state.get('confirm_delete', False):
                with st.spinner("Deleting all documents..."):
                    try:
                        # Corrected URL to include /api prefix
                        response = requests.delete(f"{FASTAPI_URL}/data")
                        if response.status_code == 200:
                            st.success("All documents deleted from the collection.")
                            st.session_state['confirm_delete'] = False  # Reset confirmation
                        else:
                            st.error(f"Failed to delete documents: {response.text}")
                    except Exception as e:
                        st.error(f"An error occurred: {str(e)}")
            else:
                st.warning("Click again to confirm deletion of all documents.")
                st.session_state['confirm_delete'] = True

    with col2:
        if st.button("Drop Entire Database", type="secondary"):
            if st.session_state.get('confirm_drop', False):
                with st.spinner("Dropping the entire database..."):
                    try:
                        # Corrected URL to include /api prefix
                        response = requests.delete(f"{FASTAPI_URL}/drop-database")
                        if response.status_code == 200:
                            st.success("Database directory successfully dropped. Restart the FastAPI server to reinitialize.")
                            st.session_state['confirm_drop'] = False # Reset confirmation
                        else:
                            st.error(f"Failed to drop database: {response.text}")
                    except Exception as e:
                        st.error(f"An error occurred: {str(e)}")
            else:
                st.warning("Click again to confirm dropping the entire database.")
                st.session_state['confirm_drop'] = True

# --- Main Interface ---
# User Query Input
st.subheader("Ask a Question")
query_text = st.text_area(
    "Enter your question here:",
    height=100,
    placeholder="e.g., What is the policy for remote work?"
)

# Button to submit query
if st.button("Get Answer", use_container_width=True, type="primary"):
    if query_text:
        with st.spinner("Searching and generating answer..."):
            try:
                # Send a POST request to the corrected FastAPI /api/ask_rag endpoint
                response = requests.post(f"{FASTAPI_URL}/ask_rag", json={"query": query_text})

                if response.status_code == 200:
                    result = response.json()
                    answer = result.get("answer")
                    documents_used = result.get("documents_used", [])

                    # Display the answer
                    st.success("Answer:")
                    st.write(answer)

                    # Display the source documents
                    st.markdown("---")
                    st.subheader("Sources Used:")
                    for doc in documents_used:
                        source = doc.get("metadata", {}).get("source", "Unknown Source")
                        content = doc.get("doc", "No content available.")
                        st.expander(f"**Source:** `{source}`").markdown(f"**Content:**\n{content}")
                else:
                    st.error(f"An error occurred with the request. Status: {response.status_code}, Detail: {response.text}")
            except requests.exceptions.ConnectionError:
                st.error("Connection error. Please ensure your FastAPI server is running.")
            except Exception as e:
                st.error(f"An unexpected error occurred: {str(e)}")
    else:
        st.warning("Please enter a question to get an answer.")

st.markdown("---")
st.info("The application connects to a FastAPI backend running on `localhost:8000/api` to handle document management and RAG.")

# Add a link to the FastAPI docs for convenience
st.markdown("For API details, visit the [FastAPI documentation](http://localhost:8000/docs).")