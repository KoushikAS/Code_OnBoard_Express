import streamlit as st
from dotenv import load_dotenv
from PyPDF2 import PdfReader
import openai
from langchain.document_loaders import TextLoader
from langchain.document_loaders.generic import GenericLoader
from langchain.document_loaders.parsers import LanguageParser
from langchain.text_splitter import CharacterTextSplitter, Language, RecursiveCharacterTextSplitter
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import FAISS
from langchain.memory import ConversationBufferMemory
from langchain.chains import ConversationalRetrievalChain, LLMChain
from langchain.chat_models import ChatOpenAI
from langchain.chains.summarize import load_summarize_chain
from htmlTemplates import bot_template, user_template, css
from langchain.prompts import PromptTemplate
from langchain.chains.combine_documents.stuff import StuffDocumentsChain
import os
from pathlib import Path
import read_gitlink


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


def get_text_from_text_files(directory):
    # Initialize an empty string to store the concatenated text
    content = ""

    # Check if directory is valid
    if not os.path.exists(directory):
        raise ValueError(f"Directory {directory} does not exist.")

    # Get a list of text files in the directory
    files = [f for f in os.listdir(directory) if os.path.isfile(os.path.join(directory, f))]

    for file in files:
        with open(os.path.join(directory, file), "r") as file_obj:
            content += file_obj.read()

    return content


def get_all_files_loader(project_name):
    # The base_path should be the path to the directory where your code files are located.
    loader = GenericLoader.from_filesystem(
        f"codes/{project_name}",  # Base directory where the code files are stored
        glob= '**/*',   # Glob pattern to recursively search for files
        # If the loader supports loading all file types without specifying suffixes, you can comment out or remove the line below.
        # If you still need to specify suffixes, list all the file extensions you're interested in.
        parser=LanguageParser(parser_threshold=500)  # Use AUTO if the parser can automatically detect the language, otherwise, you may need separate parsers for each language type
    )
    #return loader.load()  # Load the files and return the parsed data
    print(loader)
    files = loader.load()  # This may not be the correct method call depending on the langchain implementation.
    print(files)

    return files 

def get_file_loader(filename,project_name):
    # The base_path should be the path to the directory where your code files are located.
    loader = GenericLoader.from_filesystem(
        f"codes/{project_name}",  # Base directory where the code files are stored
        glob= '**/*/'+filename, 
        # If the loader supports loading all file types without specifying suffixes, you can comment out or remove the line below.
        # If you still need to specify suffixes, list all the file extensions you're interested in.
        parser=LanguageParser(parser_threshold=500)  # Use AUTO if the parser can automatically detect the language, otherwise, you may need separate parsers for each language type
    )
    #return loader.load()  # Load the files and return the parsed data

    files = loader.load()  # This may not be the correct method call depending on the langchain implementation.

    return files 

def generate_glob_pattern_for_all_subdirectories(base_directory):
    """
    Generate a glob pattern for files in all subdirectories of the base directory.

    :param base_directory: The base directory to start the glob pattern from.
    :return: A glob pattern string.
    """
    # The '**' matches any files and any directories and subdirectories underneath the base directory
    # The '*' matches any file within these directories
    glob_pattern = os.path.join(base_directory, '**', '*')
    return glob_pattern

# # Example usage:
# base_directory = "codes"  # Replace with your actual base directory
# glob_pattern = generate_glob_pattern_for_all_subdirectories(base_directory)
# print(f"Glob pattern for all subdirectories: '{glob_pattern}'")

def summarise_file(project_name):
    prompt_template = """generate technical documentation for a junior software engineer for the below code base by giving a technical details for each file independently:
            "{text}"
            :"""
    prompt = PromptTemplate.from_template(prompt_template)

    llm = ChatOpenAI(temperature=0, model_name="gpt-3.5-turbo-16k")
    llm_chain = LLMChain(llm=llm, prompt=prompt)
    stuff_chain = StuffDocumentsChain(llm_chain=llm_chain, document_variable_name="text")

    docs = get_all_files_loader(project_name)

    print(docs)
    print("waiting")
    summary_text = stuff_chain.run(docs)
    print("done")
    f = open("summary/summary.txt", "a+")
    f.write(summary_text)
    f.close()



def summarise_depth(project_name):
    prompt_template = """generate technical documentation for a junior software engineer for the below code base by giving a technical details for each file independently:
            "{text}"
            :"""
    prompt = PromptTemplate.from_template(prompt_template)

    llm = ChatOpenAI(temperature=0, model_name="gpt-3.5-turbo-16k")
    llm_chain = LLMChain(llm=llm, prompt=prompt)
    stuff_chain = StuffDocumentsChain(llm_chain=llm_chain, document_variable_name="text")

    directory_path = 'codes/'

    # Create a Path object for the directory
    directory = Path(directory_path)

    # Recursively list all filenames in the directory and its subdirectories
    # for file_path in directory.rglob('*'):
    #     if file_path.is_file():
    #         print(file_path)
    #         filename = file_path.name
        
    #         relative_file_path = os.path.relpath(filename, directory_path)
    #         summary_file = open(f"summary/summary_{os.path.basename(filename)}.txt", "a+")

    #         docs = get_file_loader(filename)
    #         summary_text = stuff_chain.run(docs)
    #         print("done")
    #         summary_file.write("\n " + os.path.basename(relative_file_path) +" :\n")
    #         summary_file.write(summary_text)
    #         summary_file.close()

    files = [f for f in os.listdir(f"codes/{project_name}") if os.path.isfile(os.path.join(f"codes/{project_name}", f))]

    for filename in files:
        summary_file = open(f"summary/summary_{filename}.txt", "a+")
        docs = get_file_loader(filename,project_name)
        print(filename)
        print(docs)
        summary_text = stuff_chain.run(docs)
        print("done")
        summary_file.write("\n " + filename +" :\n")
        summary_file.write(summary_text)
        summary_file.close() #just added


def get_text_chunks(raw_text):
    ## create a new instance 
    text_splitter = CharacterTextSplitter(separator="\n", chunk_size=1000, chunk_overlap=200, length_function=len)

    chunks = text_splitter.split_text(raw_text)  ## returns a list of chunks with each chunk size 100

    return chunks


def get_vectorstore(text_chunks):
    embeddings = OpenAIEmbeddings()
    vectorstore = FAISS.from_texts(texts=text_chunks, embedding=embeddings)

    return vectorstore


def get_conversation_chain(vectorstore):
    llm = ChatOpenAI(model_name='gpt-3.5-turbo', temperature=0.1)
    memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)
    ## initialize the conversation chain
    converstation_chain = ConversationalRetrievalChain.from_llm(
        llm=llm,
        retriever=vectorstore.as_retriever(),
        memory=memory
    )

    return converstation_chain


def handle_user_input(user_question):
    print(st)
    response = st.session_state.conversation({'question': user_question})

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

        git_link = st.text_input("Enter github URL")

        if st.button("Short Summary"):
            with st.spinner("Summarising"):
                project_name = read_gitlink.downloadRepo(git_link)
                summarise_file(project_name)

        if st.button("Indepth Summary"):
            with st.spinner("Summarising"):
                project_name = read_gitlink.downloadRepo(git_link)
                summarise_depth(project_name)

        if st.button("Add knowledge"):
            with st.spinner("Processing"):

                raw_text = get_text_from_text_files('summary/')

                ## get the text chunks
                text_chunks = get_text_chunks(raw_text)

                ## create vector store
                vectorstore = get_vectorstore(text_chunks)

                ## semantic search

                ## create conversation chain
                # session state lets streamlit know that this variable should not be reinitialized in this session
                # the reinitialization could be triggered each time we click on 'Process'
                # if we set the session state we can also use it outside of scope (outside of 'Process')
                # if we are using sessiom state initialize it before

                st.session_state.conversation = get_conversation_chain(vectorstore)

    user_question = st.text_input("Ask a question:")
    if user_question:
        handle_user_input(user_question)


if __name__ == "__main__":
    main()
