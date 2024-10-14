import openai
import streamlit as st
import os
import fitz  # PyMuPDF
from Job_Description_Scraper import fetch_job_description

# Set up Azure OpenAI API key and endpoint
openai.api_type = "azure"
openai.api_key = "7ee83affee814750af3372106d0c5a12"
openai.api_base = "https://curious-us.openai.azure.com/"
openai.api_version = "2023-03-15-preview"

# Streamlit App
st.title("Resume Builder App")

# Function to read text from a PDF file
def read_pdf(file):
    try:
        # Use fitz.open() with the file-like object
        pdf_document = fitz.open(stream=file.read(), filetype="pdf")
        text = ""
        for page in pdf_document:
            text += page.get_text()
        pdf_document.close()
        return text
    except Exception as e:
        st.error(f"An error occurred while reading the PDF file: {e}")
        return None

# Function to read text from a text file
def read_text_file(file):
    try:
        return file.read().decode("utf-8")  # Attempt to decode as UTF-8
    except UnicodeDecodeError:
        # If it fails, try with a different encoding (e.g., ISO-8859-1)
        try:
            return file.read().decode("ISO-8859-1")
        except Exception as e:
            st.error(f"An error occurred while reading the text file: {e}")
            return None

# File uploader for resume (PDF and TXT formats)
uploaded_file = st.file_uploader("Upload your resume (PDF or TXT format):", type=["pdf", "txt"])

# Initialize default_resume
default_resume = ""

# Check if a file is uploaded
if uploaded_file is not None:
    if uploaded_file.type == "application/pdf":
        default_resume = read_pdf(uploaded_file)
    elif uploaded_file.type == "text/plain":
        default_resume = read_text_file(uploaded_file)
    
    if default_resume:
        st.success("Resume uploaded successfully!")
    else:
        st.error("Failed to read the resume.")

# Setting up the system prompt using the content of the resume if available
if default_resume:
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
else:
    st.warning("Please upload a resume to continue.")

# User Interface Elements in Streamlit
user_query = ""

# Add the option to enter a URL for fetching the job description only if the resume is uploaded
if default_resume:
    st.write("Enter a URL to fetch the job description automatically:")
    job_url = st.text_input("Job Posting URL:", "")
    show_jd = st.button("Show Job Description")  # Button to display the fetched job description

    # Check if a URL is provided, and fetch the job description if it is
    if job_url:
        fetched_job_description = fetch_job_description(job_url)
        if "error" in fetched_job_description.lower():
            st.error(fetched_job_description)  # Display error if there's a problem fetching
        else:
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
#     if show_jd and submit_button:  # If the user clicks the "Show Job Description" button
#         st.warning("Please enter a valid job description.")
