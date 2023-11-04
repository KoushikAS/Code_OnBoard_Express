import streamlit as st
from dotenv import load_dotenv
from PyPDF2 import PdfReader
import openai
from langchain.text_splitter import CharacterTextSplitter
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import FAISS
from langchain.memory import ConversationBufferMemory
from langchain.chains import ConversationalRetrievalChain
from langchain.chat_models import ChatOpenAI
from htmlTemplates import bot_template,user_template,css

def get_pdf_text(pdf_docs):
    ### returns a single string with all the raw text from pdfs
    text = ""
    for pdf in pdf_docs:
        ## initialize a pdf reader object 
        pdf_reader = PdfReader(pdf)
        ## now loop through the pages in the pdf 
        for page in pdf_reader.pages:
            text += page.extract_text()
    return text

def get_text_chunks(raw_text):
    ## create a new instance 
    text_splitter = CharacterTextSplitter(separator="\n", chunk_size=1000,chunk_overlap=200, length_function=len)

    chunks = text_splitter.split_text(raw_text) ## returns a list of chunks with each chunk size 100

    return chunks  

def get_vectorstore(text_chunks):
    embeddings = OpenAIEmbeddings()
    vectorstore = FAISS.from_texts(texts=text_chunks, embedding=embeddings)

    return vectorstore

def get_conversation_chain(vectorstore):
    llm = ChatOpenAI(model_name='gpt-3.5-turbo', temperature=0.1)
    memory = ConversationBufferMemory(memory_key="chat_history",return_messages=True) 
    ## initialize the conversation chain
    converstation_chain = ConversationalRetrievalChain.from_llm(
        llm=llm,
        retriever=vectorstore.as_retriever(),
        memory=memory
    )

    return converstation_chain

def handle_user_input(user_question):
    print(st)
    response = st.session_state.conversation({'question':user_question})

    # Update the chat history
    st.session_state.chat_history = response['chat_history']

    # Add the response to the UI
    for i, message in enumerate(st.session_state.chat_history):
        # Check if the message is from the user or the chatbot
        if i % 2 == 0:
            # User message
            st.write(user_template.replace(
                "{{MSG}}", message.content), unsafe_allow_html=True)
        else:
            # Chatbot message
            st.write(bot_template.replace(
                "{{MSG}}", message.content), unsafe_allow_html=True)


def main():
    ## this allows langchain access to the access tokens.Since we are using langchain , follow the same variable format
    load_dotenv()  
    st.set_page_config(page_title="ProductDoc",page_icon=":books:")

    st.write(css, unsafe_allow_html=True)


    if "conversation" not in st.session_state:
        st.session_state.conversation = None
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = None

    st.header("Chat - Company :documents:") ## :books: is the emoji for books

    with st.sidebar:
        st.subheader("Your documents")
        pdf_docs = st.file_uploader("Upload your pdfs here and click on 'Process'", accept_multiple_files=True)   ## allows you to upload files 
        if st.button("Process"):
            with st.spinner("Processing"):    ## all the processes under this will be happening while a spinner spins - benefit of the user  
                ## get pdf text

                raw_text = get_pdf_text(pdf_docs)

                ## get the text chunks
                text_chunks = get_text_chunks(raw_text)

                ## create vector store
                vectorstore = get_vectorstore(text_chunks)

                ## semantic search 

                ## create conversation chain
                #session state lets streamlit know that this variable should not be reinitialized in this session
                # the reinitialization could be triggered each time we click on 'Process'
                # if we set the session state we can also use it outside of scope (outside of 'Process')
                # if we are using sessiom state initialize it before 

                st.session_state.conversation = get_conversation_chain(vectorstore)

    user_question = st.text_input("Ask a question:")
    if user_question:
        handle_user_input(user_question)


if __name__ == "__main__":
    main()