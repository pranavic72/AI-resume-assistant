import streamlit as st
from chatbot import get_response
from retriever import add_file_to_collection, remove_file_from_collection

# Page setup
st.set_page_config(
    page_title="Resume Assistant",
    page_icon="💼",
    layout="wide"
)

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []
if "uploaded_files" not in st.session_state:
    st.session_state.uploaded_files = []

# ---- SIDEBAR ----
with st.sidebar:
    st.title("Resume Assistant")
    st.divider()

    # File upload
    st.subheader("📁 Uploaded Files")

    uploaded = st.file_uploader(
        "Upload CVs or Resumes",
        type=["pdf", "docx"],
        accept_multiple_files=True,
        label_visibility="collapsed"
    )

    # Handle new file uploads
    if uploaded:
        for file in uploaded:
            if file.name not in st.session_state.uploaded_files:
                file_bytes = file.read()
                success = add_file_to_collection(file.name, file_bytes)
                if success:
                    st.session_state.uploaded_files.append(file.name)

    # Show uploaded files with delete buttons
    if st.session_state.uploaded_files:
        for filename in st.session_state.uploaded_files.copy():
            col1, col2 = st.columns([4, 1])
            with col1:
                ext = "📄" if filename.endswith(".docx") else "📋"
                st.markdown(f"{ext} {filename}")
            with col2:
                if st.button("❌", key=f"delete_{filename}"):
                    remove_file_from_collection(filename)
                    st.session_state.uploaded_files.remove(filename)
                    st.rerun()
    else:
        st.info("No files uploaded yet")

# ---- MAIN AREA ----
st.title("💼 Recruiter Mode")
st.markdown("Upload candidate resumes and ask anything about them.")

st.divider()

# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Chat input
if prompt := st.chat_input("Ask about candidates... e.g. Who has the most Python experience?"):
    if not st.session_state.uploaded_files:
        st.warning("Please upload at least one file first!")
    else:
        # Show user message
        with st.chat_message("user"):
            st.markdown(prompt)

        st.session_state.messages.append({
            "role": "user",
            "content": prompt
        })

        # Get response
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                response = get_response(
                    prompt,
                    st.session_state.messages,
                    mode="recruiter",
                    filenames=st.session_state.uploaded_files
                )
            st.markdown(response)

        st.session_state.messages.append({
            "role": "assistant",
            "content": response
        })