from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
import os.path
import pickle
import html
import os
import json
import base64
import logging
import markdown

SCOPES = ['https://www.googleapis.com/auth/blogger']

# Get credentials from environment variables
CLIENT_ID = os.getenv('GOOGLE_CLIENT_ID')
CLIENT_SECRET = os.getenv('GOOGLE_CLIENT_SECRET')
BLOG_ID = os.getenv('BLOGGER_BLOG_ID')

if not CLIENT_ID or not CLIENT_SECRET:
    raise ValueError("Please set GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET environment variables")
if not BLOG_ID:
    raise ValueError("Please set BLOGGER_BLOG_ID environment variable")

def get_blogger_credentials():
    """Gets valid user credentials from storage or initiates OAuth2 flow."""
    creds = None
    token_b64 = os.getenv('BLOGGER_TOKEN_PICKLE_B64')
    if token_b64:
        creds = pickle.loads(base64.b64decode(token_b64))
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            client_config = {
                "web": {
                    "client_id": CLIENT_ID,
                    "client_secret": CLIENT_SECRET,
                    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                    "token_uri": "https://oauth2.googleapis.com/token",
                    "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
                    "redirect_uris": ["http://localhost"]
                }
            }
            flow = InstalledAppFlow.from_client_config(
                client_config,
                SCOPES
            )
            creds = flow.run_local_server(port=0)
    return creds

def post_to_blogger(title, content, blog_id):
    """
    Posts content to Blogger.
    
    Args:
        title (str): The title of the blog post
        content (str): The content of the blog post in markdown format
        blog_id (str): The ID of the Blogger blog
    
    Returns:
        dict: The response from the Blogger API
    """
    try:
        creds = get_blogger_credentials()
        service = build('blogger', 'v3', credentials=creds)
        
        # Convert markdown to HTML
        html_content = markdown.markdown(content)
        
        post = {
            'kind': 'blogger#post',
            'title': title,
            'content': html_content,
            'labels': ['부동산', '아파트', '서울']
        }
        
        # Create the post
        response = service.posts().insert(
            blogId=blog_id,
            isDraft=False,
            body=post
        ).execute()
        
        logging.info(f"Post created successfully! Post ID: {response['id']}, URL: {response['url']}")
        return response
    
    except Exception as e:
        logging.error(f"An error occurred while posting to Blogger: {str(e)}")
        return None

def main():
    # Example usage
    title = "Test Post"
    content = """This is a test post.
    
    With multiple lines.
    
    And some content."""
    
    result = post_to_blogger(title, content, BLOG_ID)
    if result:
        print(f"Post created successfully! Post ID: {result['id']}")
        print(f"Post URL: {result['url']}")

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    main() 