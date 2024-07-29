import os
from dotenv import find_dotenv, load_dotenv
import openai
from langchain.chat_models import ChatOpenAI
from langchain.document_loaders import PyPDFLoader, Docx2txtLoader, TextLoader
from langchain.text_splitter import CharacterTextSplitter
from langchain.vectorstores import Chroma
from langchain.embeddings import OpenAIEmbeddings
from langchain.chains import ConversationalRetrievalChain
import streamlit as st
from streamlit_chat import message  # Ensure streamlit_chat is installed

# Load environment variables
load_dotenv(find_dotenv())
openai.api_key = os.getenv("OPENAI_API_KEY")

# Initialize OpenAI Chat model
llm_model = "gpt-3.5-turbo"
llm = ChatOpenAI(temperature=0.0, model=llm_model)

# Function to load documents (assuming documents are stored locally in the 'docs' directory)
def load_docs():
    documents = []
    doc_paths = ['./docs/' + file for file in os.listdir('./docs') if file.endswith(('.pdf', '.docx', '.txt'))]
    for path in doc_paths:
        if path.endswith('.pdf'):
            loader = PyPDFLoader(path)
        elif path.endswith('.docx'):
            loader = Docx2txtLoader(path)
        else:
            loader = TextLoader(path)
        documents.extend(loader.load())
    return documents

documents = load_docs()

# Split documents into manageable chunks
text_splitter = CharacterTextSplitter(chunk_size=1200, chunk_overlap=10)
docs = text_splitter.split_documents(documents)

# Create a vector database using Chroma
vectordb = Chroma.from_documents(
    documents=docs,
    embedding=OpenAIEmbeddings(),
    persist_directory='./data'
)
vectordb.persist()

# Initialize a conversational retrieval chain
qa_chain = ConversationalRetrievalChain.from_llm(
    llm,
    vectordb.as_retriever(search_kwargs={'k': 6}),
    return_source_documents=True,
    verbose=False
)

@st.cache_resource(show_spinner=False)
def load_data():
    with st.spinner(text="Loading and indexing the Streamlit docs – hang tight! This should take 1-2 minutes."):
        #reader = SimpleDirectoryReader(input_dir="./data", recursive=True)
        #docs = reader.load_data()
        # llm = OpenAI(model="gpt-3.5-turbo", temperature=0.5, system_prompt="You are an expert o$
        # index = VectorStoreIndex.from_documents(docs)
        #service_context = ServiceContext.from_defaults(llm=OpenAI(model="gpt-3.5-turbo", temperature=0.5, system_prompt="You are an expert on the Streamlit Python library and your job is to answer technical questions. Assume that all questions are related to the Streamlit Python library. Keep your answers technical and based on facts – do not hallucinate features."))
        index = qa_chain
        return index

index = load_data()

# Streamlit front-end setup
st.set_page_config(page_title="Chat with the Student AI Assistant, powered by UOP", page_icon="💼", layout="centered", initial_sidebar_state="auto", menu_items=None)
st.title("Student Support AI Assistant 🎓")
st.header("Ask me anything about university life, resources, and support services!")

if 'generated' not in st.session_state:
    st.session_state['generated'] = []
    
if 'past' not in st.session_state:
    st.session_state['past'] = []
    
def get_query():
    input_text = st.chat_input("Ask a question about student services...")
    return input_text

# Handle user input
user_input = get_query()
if user_input:
    # Assume 'question' and 'chat_history' keys are needed based on your previous implementation
    result = index({'question': user_input, 'chat_history': []})
    if 'answer' in result:
        st.session_state.past.append(user_input)
        st.session_state.generated.append(result['answer'])
    else:
        st.error("Sorry, I couldn't find an answer. Please try a different question.")

# Display past queries and responses
if st.session_state['generated']:
    for i in range(len(st.session_state['generated'])):
        message(st.session_state['generated'][i], key=str(i))
        message(st.session_state['past'][i], is_user=True, key=str(i) + '_user')
