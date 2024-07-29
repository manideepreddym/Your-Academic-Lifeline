import os
from langchain.document_loaders import PyPDFLoader, Docx2txtLoader, TextLoader
import streamlit as st

# Decorator to cache data, improve loading times on re-runs
@st.cache(allow_output_mutation=True, suppress_st_warning=True)
def load_docs(directory='docs'):
    documents = []
    # Construct the full path to the directory
    full_path = os.path.join(os.getcwd(), directory)
    # Check if the directory exists
    if not os.path.exists(full_path):
        st.error("Directory does not exist: " + directory)
        return []

    # Iterate over each file in the directory
    for file in os.listdir(full_path):
        file_path = os.path.join(full_path, file)
        try:
            if file.endswith('.pdf'):
                loader = PyPDFLoader(file_path)
                documents.extend(loader.load())
            elif file.endswith('.docx') or file.endswith('.doc'):
                loader = Docx2txtLoader(file_path)
                documents.extend(loader.load())
            elif file.endswith('.txt'):
                loader = TextLoader(file_path)
                documents.extend(loader.load())
        except Exception as e:
            # Logging or handling the exception
            print(f"Failed to load {file}: {str(e)}")

    return documents
