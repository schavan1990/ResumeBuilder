import requests
from bs4 import BeautifulSoup
import openai

# Set up Azure OpenAI API key and endpoint
openai.api_type = "azure"
openai.api_key = "7ee83affee814750af3372106d0c5a12"
openai.api_base = "https://curious-us.openai.azure.com/"
openai.api_version = "2023-03-15-preview"

def fetch_job_description(url):
    """
    Fetches the job description from the given URL and restructures it using OpenAI.

    Args:
    - url (str): The URL of the job posting.

    Returns:
    - str: The restructured job description text.
    """
    try:
        # Step 1: Fetch the job description from the URL
        response = requests.get(url)
        response.raise_for_status()  # Check if the request was successful
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Extracting text from the entire page (can be refined based on job site structure)
        job_description = soup.get_text().strip()

        # If no description is found, return an error message
        if not job_description:
            return "No job description found on the page."

        # Step 2: Prepare the system prompt
        system_prompt = (
            "Extract all useful information from the given job description that can help customize a resume. This includes, but is not limited to, the following sections: "
            "1. **Job Description**: Overview of the role and what the company is looking for. "
            "2. **What You Bring**: The qualifications, experience, and skills the ideal candidate should have. "
            "3. **What You'll Do**: Key responsibilities and duties of the role. "
            "4. **Requirements**: Essential and preferred qualifications, certifications, or education needed for the job. "
            "5. **Skills Needed**: The technical and soft skills required for the job. "
            "6. **Responsibilities**: The tasks and duties the candidate will undertake. "
            "In addition to these sections, look for any other relevant information that can help in customizing a resume for this position. "
            "This might include key achievements, company values, industry-specific terminology, and other details that will help align the resume "
            "with the job. Extract everything that could help highlight the candidate’s qualifications, skills, and experiences that match the job description. "
            "Your goal is to provide a clear, concise, and comprehensive breakdown of the job description that will allow the resume to be fully optimized "
            "for ATS while aligning it with the job requirements. "
            "The resume will be restructured into the following format: Professional Summary, Professional Experience, Education, Certifications, and Awards/Projects. "
            "Please ensure all the information you extract is relevant to resume customization, ATS optimization, and the job description provided. "
        )

        # Step 3: Pass the job description to OpenAI for restructuring
        response = openai.ChatCompletion.create(
                    deployment_id="gpt-4o",  # Use the correct deployment ID for your Azure instance
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": job_description}
                    ],
                    # max_tokens=250,
                    temperature=0.7
                )

        # Extract the restructured text from the response
        restructured_description = response['choices'][0]['message']['content'].strip()
        return restructured_description

    except requests.exceptions.RequestException as e:
        return f"An error occurred while fetching the job description: {str(e)}"
    except openai.error.OpenAIError as e:
        return f"An error occurred with OpenAI API: {str(e)}"

# # Example usage:
# job_url = 'https://example.com/job-posting-url'  # Replace with the actual job posting URL
# restructured_job_description = fetch_job_description(job_url)
# print("Restructured Job Description:")
# print(restructured_job_description)
