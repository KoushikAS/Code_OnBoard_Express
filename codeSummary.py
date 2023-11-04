import streamlit as st
from dotenv import load_dotenv
import requests
import base64
import os
from urllib.parse import urlparse, urljoin
from langchain.chat_models import ChatOpenAI
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
# Load environment variables
load_dotenv()

# GitHub API URL
GITHUB_API_URL = 'https://api.github.com/'

# Initialize the ChatOpenAI model
llm = ChatOpenAI(model_name='gpt-3.5-turbo', temperature=0.1)

# Function to summarize text using the ChatOpenAI model
def summarize_text(text):
    response = llm.generate(
        f"Summarize this code:\n\n{text}", 
        max_tokens=150  # You can adjust the max_tokens if necessary
    )
    return response['choices'][0]['message']['content'].strip()

# Function to parse GitHub repo URL
def parse_github_repo_url(repo_url):
    path_parts = urlparse(repo_url).path.strip('/').split('/')
    if len(path_parts) >= 2:
        return path_parts[0], path_parts[1]
    else:
        raise ValueError("Invalid GitHub repository URL.")

# Function to get files from GitHub repo
def get_files_from_repo(repo_url, token, extensions):
    owner, repo = parse_github_repo_url(repo_url)
    api_url = f"repos/{owner}/{repo}/git/trees/main?recursive=1"
    headers = {'Authorization': f'token {token}'}
    response = requests.get(urljoin(GITHUB_API_URL, api_url), headers=headers)
    response.raise_for_status()

    tree = response.json()['tree']
    file_paths = [
        item['path'] for item in tree
        if item['type'] == 'blob' and any(item['path'].endswith(ext) for ext in extensions)
    ]

    return file_paths

# Function to get the content of a file from GitHub
def get_file_content(owner, repo, file_path, token):
    api_url = f"repos/{owner}/{repo}/contents/{file_path}"
    headers = {'Authorization': f'token {token}'}
    response = requests.get(urljoin(GITHUB_API_URL, api_url), headers=headers)
    response.raise_for_status()

    content_data = response.json()
    if content_data.get('encoding') == 'base64':
        content = base64.b64decode(content_data['content']).decode('utf-8')
    else:
        content = content_data['content']
    return content

# Function to get GitHub file contents and summarize them
def get_github_files_and_summarize(repo_url, token, extensions):
    file_contents = []
    try:
        owner, repo = parse_github_repo_url(repo_url)
        file_paths = get_files_from_repo(repo_url, token, extensions)
        for file_path in file_paths:
            content = get_file_content(owner, repo, file_path, token)
            # Summarize content using the ChatOpenAI model
            summary = summarize_text(content)
            file_contents.append((file_path, summary))
    except Exception as e:
        st.error(f"An error occurred: {e}")
    return file_contents

# Main Streamlit app function
def main():
    # Your existing main function code...
     ## this allows langchain access to the access tokens.Since we are using langchain , follow the same variable format
    load_dotenv()  
    st.set_page_config(page_title="ProductDoc",page_icon=":books:")

    st.write(css, unsafe_allow_html=True)


    if "conversation" not in st.session_state:
        st.session_state.conversation = None
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = None

    st.header("Chat - Company :documents:") ## :books: is the emoji for books

    # Sidebar for GitHub repo URL and file extensions
    with st.sidebar:
        st.subheader("GitHub Repository Summarizer")
        repo_url = st.text_input("Enter the GitHub repository URL")
        extensions = st.text_input("File extensions", value='.py,.js,.java,.cpp,.h', help="Enter comma-separated file extensions")
        if repo_url and st.button("Fetch and Summarize"):
            with st.spinner("Fetching files and summarizing..."):
                extensions_list = extensions.split(',')
                # Use your GitHub token from environment variables or enter it manually
                token = os.getenv('GITACC_TOKEN')
                file_summaries = get_github_files_and_summarize(repo_url, token, extensions_list)
                # Display summaries in Streamlit
                for file_path, summary in file_summaries:
                    st.write(f"### {file_path}")
                    st.write(summary)

# Running the Streamlit app
if __name__ == "__main__":
    main()
