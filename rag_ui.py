# import streamlit as st
# import requests

# # --- Hide Streamlit default UI ---
# hide_streamlit_style = """
#     <style>
#     # MainMenu {visibility: hidden;}
#     footer {visibility: hidden;}

#     </style>
# """
# st.markdown(hide_streamlit_style, unsafe_allow_html=True)

# # --- Config ---
# BASE_URL = "http://127.0.0.1:8000/api"  # FastAPI backend

# st.set_page_config(
#     page_title="Q&A System",
#     page_icon="🤖",
#     layout="wide"
# )

# # --- Sidebar ---
# st.sidebar.title("⚙️ Settings")
# mode = st.sidebar.radio(
#     "Select response type:",
#     ("Based on my documents", "General response")
# )

# st.sidebar.info(
#     f"Backend: {BASE_URL}"
# )

# # --- Main UI ---
# st.title("🤖 Q&A System")
# st.markdown("Type your question below and choose the mode from the sidebar.")

# # query = st.text_area("💬 Your Question:", placeholder="e.g., كيف يتم التعامل مع حالات الطوارئ؟")
# query = st.text_area("💬 Your Question:")
# ask_btn = st.button("🔎 Get Answer", use_container_width=True, type="primary")

# if ask_btn and query.strip():
#     with st.spinner("⚡ Fetching answer..."):
#         try:
#             if mode == "Based on my documents":
#                 endpoint = f"{BASE_URL}/ask-rag"
#                 payload = {"query": query}
#             else:
#                 endpoint = f"{BASE_URL}/ask-gemini"
#                 payload = {"question": query}

#             response = requests.post(endpoint, json=payload)

#             if response.status_code == 200:
#                 data = response.json()

#                 # --- Answer box ---
#                 st.markdown("### ✅ Answer")
#                 st.success(data.get("answer", "No answer returned."))

#                 # # --- Sources (only in RAG mode) ---
#                 # if mode == "Based on my documents" and "sources" in data:
#                 #     st.markdown("### 📚 Sources used")
#                 #     for src in data["sources"]:
#                 #         with st.expander(f"{src.get('filename', 'Unknown file')} | {src.get('section','')}"):
#                 #             st.write(src.get("text", ""))

#             else:
#                 st.error(f"❌ Error {response.status_code}: {response.text}")

#         except Exception as e:
#             st.error(f"⚠️ Failed to connect to backend: {e}")


# streamlit_app.py
import streamlit as st
import requests

# --- Hide Streamlit default UI ---
hide_streamlit_style = """
    <style>
    # MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    </style>
"""
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

# --- Config ---
BASE_URL = "http://127.0.0.1:8000/api"

st.set_page_config(
    page_title="Q&A System",
    page_icon="🤖",
    layout="wide"
)

# --- Sidebar ---
st.sidebar.title("⚙️ Settings")
mode = st.sidebar.radio(
    "Select response type:",
    ("Based on my documents", "General response")
)

st.sidebar.info(f"Backend: {BASE_URL}")

# --- Main UI ---
st.title("🤖 Q&A System")
st.markdown("Type your question below and choose the mode from the sidebar.")

query = st.text_area("💬 Your Question:")
ask_btn = st.button("🔎 Get Answer", use_container_width=True, type="primary")

if ask_btn and query.strip():
    with st.spinner("⚡ Fetching answer..."):
        try:
            if mode == "Based on my documents":
                endpoint = f"{BASE_URL}/ask-rag"
                payload = {"query": query}
            else:
                endpoint = f"{BASE_URL}/ask-gemini"
                payload = {"question": query}

            response = requests.post(endpoint, json=payload)

            if response.status_code == 200:
                data = response.json()
                answer = data.get("answer", "")

                # --- Render Answer ---
                st.markdown("### ✅ Answer")
                st.markdown(answer, unsafe_allow_html=True)  # allows table rendering

                # --- Debug context in expander ---
                # if "context_used" in data:
                #     with st.expander("📚 Debug: Retrieved Context"):
                #         st.text(data["context_used"])

            else:
                st.error(f"❌ Error {response.status_code}: {response.text}")

        except Exception as e:
            st.error(f"⚠️ Failed to connect to backend: {e}")
