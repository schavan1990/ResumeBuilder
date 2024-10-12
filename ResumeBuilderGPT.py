import openai
import streamlit as st
import os

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

# User Interface Elements in Streamlit
st.write("Please enter Job Description to generate a tailored resume:")
user_query = st.text_input("Job Description :", "")
submit_button = st.button("Submit")

if submit_button:
    if user_query:
        # Generating response using Azure OpenAI's GPT-4 model
        try:
            response = openai.ChatCompletion.create(
                deployment_id="gpt-4o",  # Use the correct deployment ID for your Azure instance
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_query}
                ],
                max_tokens=150,
                temperature=0.7
            )
            assistant_response = response['choices'][0]['message']['content'].strip()
            st.write(assistant_response)
        except Exception as e:
            st.error(f"An error occurred: {str(e)}")
    else:
        st.warning("Please enter a query before submitting.")
