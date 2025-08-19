import streamlit as st
import requests

# Hide Streamlit's deploy button and menu
hide_streamlit_style = """
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    </style>
"""
st.markdown(hide_streamlit_style, unsafe_allow_html=True)


# --- Config ---
BASE_URL = "http://127.0.0.1:8000/api"  # FastAPI backend

st.set_page_config(
    page_title="Q&A System",
      page_icon="🤖",
    layout="wide"
)

# --- Sidebar ---
st.sidebar.title("Choose Your Mode")
mode = st.sidebar.radio(
    "Select the type of response you want:",
    ("Based on my documents", "General response")
)

st.sidebar.info(
    f"The application is configured to connect to your FastAPI backend at {BASE_URL}."
)

# --- Main UI ---
st.title("🤖 Welcome to Q&A System")
st.write("Ask a question and choose your preferred mode in the sidebar to get an answer.")

query = st.text_area("Enter your question here:", placeholder="e.g., What is the policy for remote work?")
ask_btn = st.button("Get Answer", use_container_width=True, type="primary")

if ask_btn and query.strip():
    with st.spinner("Fetching answer..."):
        try:
            if mode == "Based on my documents":
                endpoint = f"{BASE_URL}/ask_rag"
                payload = {"query": query}
            else:
                endpoint = f"{BASE_URL}/ask-gemini"
                payload = {"question": query}

            response = requests.post(endpoint, json=payload)

            if response.status_code == 200:
                data = response.json()
                st.subheader("Answer")
                st.write(data.get("answer", "No answer returned."))

                # Optional: show retrieved documents only in "Based on my documents" mode
                # if mode == "Based on my documents" and "documents_used" in data:
                    # with st.expander("📄 Documents Used"):
                    #     for i, doc in enumerate(data["documents_used"]):
                    #         st.markdown(f"**Source {i+1}:** {doc['metadata'].get('source','unknown')}")
                    #         st.text_area(
                    #             f"Document {i+1}",
                    #             value=doc["doc"],
                    #             height=150,
                    #             key=f"doc_{i}"
                    #         )
            else:
                st.error(f"Error {response.status_code}: {response.text}")

        except Exception as e:
            st.error(f"Failed to connect to backend: {e}")
