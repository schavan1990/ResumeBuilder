import requests
from bs4 import BeautifulSoup

def fetch_job_description(url):
    """
    Fetches and returns the job description from the given URL.
    
    Args:
    - url (str): The URL of the job posting.

    Returns:
    - str: The job description text if found, or an error message.
    """
    try:
        response = requests.get(url)
        response.raise_for_status()  # Check if the request was successful
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Extracting text from the entire page (can be refined based on job site structure)
        job_description = soup.get_text()
        return job_description.strip()

    except requests.exceptions.RequestException as e:
        return f"An error occurred while fetching the job description: {str(e)}"
