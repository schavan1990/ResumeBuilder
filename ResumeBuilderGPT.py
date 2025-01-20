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
        You are an expert in resume optimization and customization, specializing in ensuring resumes are 95% or more compatible with ATS (Applicant Tracking System) requirements for specific job descriptions. Your task is to receive a job description and a base resume, customize the resume to align perfectly with the job description, and evaluate the keyword matches between the job description and the updated resume.  

        Your key objective is to maximize ATS relevance by exactly matching keywords and phrases from the job description within the provided JSON structure. **Do not modify the JSON structure**—any change to the format will break PDF generation.  

        **Customization Guidelines:**  
        - **No Achievement Left Unmodified**: Every achievement in the **Experience** section must be revised to reflect the job description's terminology. Only achievements that already match perfectly should remain unchanged.  
        - **Prioritize Keywords**: Extract critical terms from the job description, including technical skills, soft skills, qualifications, tools, and industry-specific language, and integrate them into the achievements naturally.  

        **Steps to Achieve High ATS Relevance:**  

        1. **Keyword Extraction and Alignment**:  
           - Identify the exact keywords and phrases from the job description.  
           - Use these keywords verbatim when modifying achievements to ensure precise matches. Avoid synonyms or paraphrasing.  

        2. **Achievement Customization**:  
           - **Restructure and Replace**: Adjust or rewrite each bullet point in the **Experience** section to include relevant keywords.  
           - Ensure the integration of both job-specific terminology and measurable outcomes. For instance, modify *"Improved team efficiency"* to *"Improved team efficiency by implementing Agile methodologies and achieving a 20% reduction in project delivery time."*  

        3. **Skills Section Enhancement**:  
           - Ensure the **Skills** section includes all relevant technical and soft skills directly listed in the job description.  

        4. **Keyword Usage Validation**:  
           - Track the number of keywords integrated into the updated resume and ensure comprehensive coverage of the job description's requirements.  
           - Highlight which achievements have been updated and the keywords added.  

        5. **Output in JSON Format Only**:  
           - Provide the updated resume in the exact JSON format below, ensuring all modifications fit within the structure:  

        ```json  
        {
          "contactInformation": {
            "name": "Name",
            "location": "Location",
            "email": "Email",
            "linkedin": "LinkedIn"
          },
          "professionalSummary": "A brief professional summary highlighting skills, experience, and career focus.",
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
              "achievements": [
                "Achievement 1",
                "Achievement 2"
              ]
            }
          ],
          "skills": [
            "Skill 1",
            "Skill 2",
            "Skill 3"
          ]
        }
        ```  

        **Reminders:**  
        - Focus on the **Experience** and **Skills** sections for maximum customization.  
        - Avoid adding new achievements; only enhance existing ones to maintain authenticity.  
        - Ensure that no section or JSON structure is modified outside of the content updates.  
        - Validate the JSON output to ensure it remains valid and properly structured.
        - Generate professionalSummary to best suit the job description and the candidate's profile.
        - The final assistant response should contain only the updated JSON output without additional comments or formatting.  

        """ + default_resume  
    )

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
                "Use this extracted information to generate a customized resume in the following format: Professional Summary, Professional Experience, Education, Certifications, Awards/Projects and Skills. "
                "Focus on highlighting aspects that will best demonstrate the candidate’s alignment with the job requirements, without returning the restructured job description anywhere in the response. "
                "Job Description is : \n" + fetched_job_description
            )

    submit_button = st.button("Submit")

    if user_query: 
        if submit_button:
            # Generating response using Azure OpenAI's GPT-4 model
            #st.write("User query with job description : " + user_query)
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
                    #st.code("Assistant response : "+assistant_response)  # Display the raw response for debugging

                    process_assistant_response(assistant_response)
                    # st.success("Resume generated and PDF created successfully!")
                except json.JSONDecodeError:
                    st.error("Failed to parse the assistant response. Ensure the response is in valid JSON format.")
                except Exception as e:
                    st.error(f"An unexpected error occurred: {str(e)}")

# ResumeBuilderGPT.py
# Purpose: It integrates Azure OpenAI GPT-4 API to customize resumes based on job descriptions.
# Features:
# Resume Upload: Allows users to upload resumes in PDF or TXT format. The content is extracted and displayed (or used internally).
# Job Description Parsing: Fetches or allows the user to input job descriptions to tailor the resume to a specific job.
# AI-Powered Optimization:
# Sends the resume and job description to Azure OpenAI GPT-4 API.
# Uses a well-defined system prompt to ensure resume achievements are rewritten for maximum relevance and ATS compatibility.
# JSON Response Parsing:
# Processes GPT-4 responses in JSON format, with specific sections like "Professional Experience" and "Education."
# Integration with PDF Generation:
# The output JSON is passed to the GeneratePDF module to create a tailored resume in PDF format.
