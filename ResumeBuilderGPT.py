import openai
import streamlit as st
import os
import streamlit as st
from Job_Description_Scraper import fetch_job_description

# # Set up Azure OpenAI API key and endpoint - make sure to replace 'your-api-key' and 'your-endpoint' with your actual API key and endpoint
# openai.api_type = "azure"
# openai.api_key = os.getenv("AZURE_OPENAI_API_KEY")
# openai.api_base = os.getenv("AZURE_OPENAI_ENDPOINT")
# openai.api_version = "2023-05-15"

# Set up Azure OpenAI API key and endpoint
openai.api_type = "azure"
openai.api_key = "7ee83affee814750af3372106d0c5a12"
openai.api_base = "https://curious-us.openai.azure.com/"
openai.api_version = "2023-03-15-preview"

# Streamlit App
st.title("Resume Builder App")

# Reading the default resume from a local file and setting up the system prompt
def read_resume(file_path):
    try:
        with open(file_path, 'r') as file:
            default_resume = file.read()
            return default_resume
    except FileNotFoundError:
        print(f"Error: The file at {file_path} was not found.")
        return None
    except Exception as e:
        print(f"An error occurred: {e}")
        return None

# Path to the local file containing the resume
file_path = "C:\\Users\\sumit\\OneDrive\\Desktop\\Ankit POC\\defaultCV.txt"


# Reading the resume from the file
default_resume = read_resume(file_path)

if default_resume:
    # Setting up the system prompt using the content of the resume
    system_prompt = (
        "You are an expert in resume optimization, specializing in customizing resumes "
        "to align with specific job descriptions while ensuring they are fully optimized "
        "for Applicant Tracking Systems (ATS). I will provide you with a job description "
        "and a resume, and your task is to tailor the resume details to make it ATS-friendly "
        "and in line with the job requirements. You are committed to delivering structured, "
        "keyword-optimized resumes that adhere to best practices, maximizing the chances of "
        "passing ATS screenings and securing interviews. My default resume is: \n"
        + default_resume
    )
    print("System prompt successfully created.")
else:
    print("Failed to create system prompt due to resume loading issues.")

# # User Interface Elements in Streamlit
# st.write("Please enter Job Description to generate a tailored resume:")
# user_query = st.text_area("Job Description:", "", height=200)  # Multi-line input field for job description 

# Initialize user_query to an empty string
user_query = ""


# Add the option to enter a URL for fetching the job description
st.write("Enter a URL to fetch the job description automatically")
job_url = st.text_input("Job Posting URL:", "")

# # Print the job_url value for debugging purposes
# st.write("Debug: Job URL entered:", job_url)  # This line will display the URL input by the user 
show_jd = st.button("Show Job Description")  # Button to display the fetched job description

# Check if a URL is provided, and fetch the job description if it is
if job_url:
    fetched_job_description = fetch_job_description(job_url)
    if "error" in fetched_job_description.lower():
        st.error(fetched_job_description)  # Display error if there's a problem fetching
    else:
        # user_query = fetched_job_description  # Autofill the text area with fetched job description
        # st.text_area("Job Description:", value=user_query, height=200)
        user_query = st.text_area("Job Description:", value=fetched_job_description, height=200, key='job_description_text_area')
        submit_button = st.button("Submit")

if user_query: 
    if submit_button:
        # Generating response using Azure OpenAI's GPT-4 model
        try:
            response = openai.ChatCompletion.create(
                deployment_id="gpt-4o",  # Use the correct deployment ID for your Azure instance
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_query}
                ],
                max_tokens=250,
                temperature=0.7
            )
            assistant_response = response['choices'][0]['message']['content'].strip()
            st.write(assistant_response)
        except Exception as e:
            st.error(f"An error occurred: {str(e)}")
    # else:
    #     st.warning("Please enter a query before submitting.")
else:
    if show_jd and submit_button: # If the user clicks the "Show Job Description" button
        st.warning("Please enter a valid job description.")
