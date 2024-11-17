import json
import openai
import streamlit as st
import os
import fitz  # PyMuPDF
from jinja2 import Template
import pdfkit  # Requires wkhtmltopdf installed locally
from Job_Description_Scraper import fetch_job_description
from GeneratePDF import process_assistant_response

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
        # st.write(default_resume)
    else:
        st.error("Failed to read the resume.")

# Setting up the system prompt using the content of the resume if available
if default_resume:
  system_prompt = (
    """ 
    You are an expert in resume optimization and customization, specializing in aligning resumes with job descriptions for maximum ATS (Applicant Tracking System) compatibility. Your task is to receive a job description and a base resume, customize the resume, and then evaluate the keyword matches between the job description and the updated resume.

    You will customize the resume to improve its relevance to the job description by **exactly** integrating keywords and other contextually relevant details that highlight the candidate’s alignment with the role. **No implied matching** is allowed—only use the exact keywords from the job description. 

    **Key Adjustments to Ensure Customization**:
    - **Modify Every Achievement**: Ensure every achievement in the **Experience** section is updated to reflect keywords and context from the job description. No bullet point should remain unmodified unless it already includes relevant job description keywords.
    - **Non-Matching Achievements**: Identify achievements that do not align closely with the job description and rewrite them to include at least one relevant keyword or phrase.

    **Steps to Follow:**

    1. **Extract Keywords**: Identify the key terms and phrases from the job description that are essential to the role, including both technical and soft skills, job-specific terminology, and qualifications. **List the exact words and phrases as they appear in the job description.**

    2. **Modify Resume Achievements**:
       - **Force a change in every achievement.** 
       - Restructure existing content to integrate job description keywords naturally.
       - Replace less relevant details with job-specific terminology to ensure alignment.
       - Do not add entirely new achievements; only modify and enhance existing ones.

    3. **Exact Keyword Integration**: Insert keywords from the job description into the achievements **as-is**, ensuring a precise match with the job description. For example:
        - If the job description requires "stakeholder management," rewrite a point to reflect this, e.g., *"Led stakeholder management initiatives, facilitating communication and project alignment."*

    4. **Keyword Match Tracking**:
        - Count the number of keywords integrated into the updated resume.
        - Identify and report which specific achievements have been modified to include these keywords.

    5. **Avoid Identical Outputs**:
        - Compare input and output resumes.
        - Ensure that no achievement remains unchanged unless it already perfectly aligns with the job description.

    6. **Output Requirements**:
        - Return the updated resume in JSON format, following this structure:

        ```json
        {
          "contactInformation": {
            "name": "Name",
            "location": "Location",
            "email": "Email",
            "linkedin": "LinkedIn"
          },
          "professionalExperience": [
            {
              "company": "Company Name",
              "role": "Role",
              "location": "Location",
              "date": "Start-End Date",
              "achievements": [
                "Achievement 1",
                "Achievement 2",
                "Achievement 3"
              ]
            }
          ],
          "education": [
            {
              "institution": "Institution Name",
              "degree": "Degree",
              "location": "Location",
              "date": "Start-End Date",
              "achievements": [
                "Achievement 1",
                "Achievement 2"
              ]
            }
          ],
          "certifications": [
            {
              "name": "Certification Name",
              "organization": "Organization"
            }
          ],
          "awardsAndProjects": [
            {
              "project": "Project Name",
              "organization": "Organization Name",
              "date": "Date",
              "location": "Location",
              "achievements": [
                "Achievement 1",
                "Achievement 2"
              ]
            }
          ],
          "currentProject": {
            "description": "Current Project Description"
          }
        }
        ```

    **Reminders**:
    - Focus exclusively on customizing the **Experience** section’s achievements.
    - Ensure that no achievement remains unchanged unless it perfectly matches the job description.
    - Highlight modified achievements and track keyword matches to ensure transparency in changes.
    - Maintain clarity, consistency, and structure in the JSON format, and ensure valid JSON output only.
    """+ default_resume )

else:
    st.warning("Please upload a resume to continue.")

# User Interface Elements in Streamlit
user_query = ""

# Add the option to enter a URL for fetching the job description only if the resume is uploaded
if default_resume:
    st.write("Enter a URL to fetch the job description automatically:")
    job_url = st.text_input("Job Posting URL:", "")
    # show_jd = st.button("Show Job Description")  # Button to display the fetched job description

   # Check if a URL is provided, and fetch the job description if it is
    if job_url:
        fetched_job_description = fetch_job_description(job_url)
        # print("Job desc: " + fetched_job_description)  # You can remove this print in production code

        # Check if the job description contains an error or is empty
        if "error" in fetched_job_description.lower() or not fetched_job_description.strip():
            st.warning("Job Description is empty or invalid.")  # Display warning if the description is empty or invalid
            user_query = st.text_area("Enter Job Description :", "")  # Text area for user query
        else:
            # Create the user query using the fetched job description
            user_query = (
                "Analyze the given job description to identify all information useful for customizing a resume that aligns with the role. "
                "Focus on capturing details relevant to optimizing the resume for ATS compatibility and tailoring it to the job requirements. "
                "Specifically, extract information for these sections: "
                "1. Job Overview "
                "2. Candidate Profile "
                "3. Key Responsibilities "
                "4. Requirements "
                "5. Core Skills "
                "6. Responsibilities and Duties "
                "In addition, gather insights on key achievements, company values, industry terminology, and other details that could enhance the resume’s relevance to the role. "
                "Use this extracted information to generate a customized resume in the following format: Professional Summary, Professional Experience, Education, Certifications, and Awards/Projects. "
                "Focus on highlighting aspects that will best demonstrate the candidate’s alignment with the job requirements, without returning the restructured job description anywhere in the response. "
                "Job Description is : \n" + fetched_job_description
            )

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
                    temperature=0.7
                )
                assistant_response = response['choices'][0]['message']['content'].strip()
                # st.write(assistant_response)
            except Exception as e:
                st.error(f"An error occurred: {str(e)}")
# else:
#     if show_jd and submit_button:  # If the user clicks the "Show Job Description" button
#         st.warning("Please enter a valid job description.")

                
# Process the assistant response with Test_Latex.py function
             # Process the assistant response with Test_Latex.py function
            if assistant_response:
                try:
                    # st.write("Assistant Response Preview:")
                    st.code(assistant_response)  # Display the raw response for debugging

                    process_assistant_response(assistant_response)
                    # st.success("Resume generated and PDF created successfully!")
                except json.JSONDecodeError:
                    st.error("Failed to parse the assistant response. Ensure the response is in valid JSON format.")
                except Exception as e:
                    st.error(f"An unexpected error occurred: {str(e)}")
