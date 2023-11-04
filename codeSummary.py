import requests
import os
from dotenv import load_dotenv
import base64
from urllib.parse import urlparse, urljoin
import openai
from read_gitlink import parse_github_repo_url, get_files_from_repo, get_file_content

# Load environment variables
load_dotenv()

# Set to GitHub's API base URL
GITHUB_API_URL = 'https://api.github.com/'
OPENAI_API_URL = 'https://api.openai.com/v1/engines/davinci-codex/completions'

def openai_summarize(code, openai_api_key):
    """
    Summarizes a piece of code using OpenAI's API.
    """
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {openai_api_key}'
    }
    data = {
        'prompt': f'Summarize this code:\n\n{code}\n\n###',
        'temperature': 0,
        'max_tokens': 150
    }
    response = requests.post(OPENAI_API_URL, json=data, headers=headers)
    response.raise_for_status()
    return response.json()["choices"][0]["text"].strip()

# Include the previous functions (parse_github_repo_url, get_files_from_repo, get_file_content)

# Example usage:
repo_url = 'https://github.com/KoushikAS/duke-ece-650-project4'
extensions = ('.cpp','.h','.py','.java')
token = os.getenv('GITACC_TOKEN')  # Replace with your GitHub token
openai_api_key = os.getenv('OPENAI_API_KEY')  # Replace with your OpenAI API key

summaries = []

try:
    owner, repo = parse_github_repo_url(repo_url)
    file_paths = get_files_from_repo(repo_url, token, extensions)
    
    for file_path in file_paths:
        content = get_file_content(owner, repo, file_path, token)
        summary = openai_summarize(content, openai_api_key)
        summaries.append(f'### File: {file_path}\nSummary:\n{summary}\n\n')

    # Combine all summaries into one document
    summary_document = "\n".join(summaries)

    # Output the combined summary
    print(summary_document)
    # Save the combined summary to a file if needed
    with open('summary_document.txt', 'w') as file:
        file.write(summary_document)

except requests.HTTPError as e:
    print(f"HTTP Error: {e.response.json()}")
except Exception as e:
    print(f"An error occurred: {e}")
