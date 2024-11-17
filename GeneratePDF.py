import json
import subprocess
import os
import logging
from jinja2 import Environment, FileSystemLoader
import streamlit as st
from io import BytesIO
import time
import base64
import streamlit.components.v1 as components  # Correct import

# Set up logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Define a function to escape LaTeX special characters
def escape_latex(value):
    """Escape LaTeX special characters in the given string."""
    if not value:
        return value
    latex_special_chars = {
        '%': r'\%',     
        '$': r'\$',     
        '&': r'\&',     
        '#': r'\#',     
        '_': r'\_',     
        '{': r'\{',     
        '}': r'\}',     
        '~': r'\textasciitilde',
        '^': r'\textasciicircum',
        '\\': r'\textbackslash',
        '\n': r'\\',  # Handling newline characters
    }
    for char, replacement in latex_special_chars.items():
        value = value.replace(char, replacement)
    return value

# Preprocess JSON to escape LaTeX characters
def preprocess_json(data):
    """Recursively escape LaTeX special characters in a dictionary or list."""
    if isinstance(data, dict):
        return {key: preprocess_json(value) for key, value in data.items()}
    elif isinstance(data, list):
        return [preprocess_json(item) for item in data]
    elif isinstance(data, str):
        return escape_latex(data)
    return data

# Function to render LaTeX from template
def render_latex_template(sections):
    """Render LaTeX content from the template using the provided sections."""
    latex_template = r"""
    \documentclass[a4paper,10pt]{article}
    \usepackage[left=1in, right=1in, top=1in, bottom=1in]{geometry}
    \usepackage{enumitem}
    \usepackage{hyperref}
    \usepackage{xcolor}
    \usepackage{times}

    \definecolor{darkblue}{RGB}{0, 0, 139}

    \pagestyle{empty}
    \begin{document}

    \begin{center}
        {\Large\textbf{ {{ contactInformation.name }} }}\\[0.5em]
        {{ contactInformation.location }}\\[0.3em]
        \href{mailto:{{ contactInformation.email }}}{ {{ contactInformation.email }} }{% if contactInformation.phone %} | {{ contactInformation.phone }}{% endif %}\\[0.3em]
        \href{ {{ contactInformation.linkedin }} }{ {{ contactInformation.linkedin }} }
    \end{center}

    \hrule
    \vspace{1em}

    \section*{Professional Experience}
    {% for experience in professionalExperience %}
        {\textbf{ {{ experience.company }} }} \hfill {\textit{ {{ experience.date }} }}\\
        {\textbf{ {{ experience.role }} }} \hfill {{ experience.location }}\\
        \begin{itemize}[leftmargin=*,nosep]
        {% for achievement in experience.achievements %}
            \item {{ achievement }}
        {% endfor %}
        \end{itemize}
    {% endfor %}

    \section*{Education}
    {% for edu in education %}
        {\textbf{ {{ edu.institution }} }} \hfill {\textit{ {{ edu.date }} }}\\
        {{ edu.degree }}{% if edu.location %}, {{ edu.location }}{% endif %}
        {% if edu.achievements %}
        \begin{itemize}[leftmargin=*,nosep]
        {% for achievement in edu.achievements %}
            \item {{ achievement }}
        {% endfor %}
        \end{itemize}
        {% endif %}
    {% endfor %}

    \section*{Certifications}
    \begin{itemize}[leftmargin=*,nosep]
    {% for cert in certifications %}
        \item {{ cert.name }}{% if cert.organization %} by {{ cert.organization }}{% endif %}
    {% endfor %}
    \end{itemize}

    \section*{Awards and Projects}
    {% for project in awardsAndProjects %}
        {\textbf{ {{ project.project }} }} \hfill {\textit{ {{ project.date }} }}\\
        {% if project.organization %}{{ project.organization }}{% endif %}{% if project.location %}, {{ project.location }}{% endif %}
        \begin{itemize}[leftmargin=*,nosep]
        {% for achievement in project.achievements %}
            \item {{ achievement }}
        {% endfor %}
        \end{itemize}
    {% endfor %}

    \section*{Current Project}
    {{ currentProject.description }}

    \end{document}
    """
    env = Environment(loader=FileSystemLoader('.'))
    template = env.from_string(latex_template)
    return template.render(**sections)

# Function to compile LaTeX and generate PDF
def compile_latex_to_pdf(tex_filename, output_dir):
    """Compile LaTeX file to PDF using xelatex and save it to a specified directory."""
    try:
        logger.debug(f"Compiling LaTeX file {tex_filename} to PDF using xelatex.")
        
        # Ensure the output directory exists
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        
        # Construct the full PDF output path
        pdf_output_path = os.path.join(output_dir, os.path.basename(tex_filename).replace('.tex', '.pdf'))

        # Run xelatex to generate the PDF
        result = subprocess.run(
            ['xelatex', '-output-directory', output_dir, '-interaction=nonstopmode', tex_filename],
            check=True, capture_output=True
        )
        
        logger.debug(f"xelatex stdout: {result.stdout.decode()}")
        logger.debug(f"xelatex stderr: {result.stderr.decode()}")  # Capture stderr for error details
        
        logger.debug("PDF generation completed.")
        return pdf_output_path

    except subprocess.CalledProcessError as e:
        logger.error(f"Error generating PDF: {e.stderr.decode()}")
        return None

# Function to convert PDF to Base64 and prepare download
def prepare_pdf_for_download(pdf_file):
    """Convert the generated PDF to Base64 and prepare it for download via file picker."""
    with open(pdf_file, "rb") as f:
        pdf_data = f.read()

    pdf_base64 = base64.b64encode(pdf_data).decode()
    logger.debug("INSIDE FINALLLYYYYYY")
    js = f"""
    <button type="button" id="picker">Download PDF</button>

    <script>
    async function run() {{
        const handle = await showSaveFilePicker({{
            suggestedName: 'resume.pdf',
            types: [{{
                description: 'PDF Resume',
                accept: {{'application/pdf': ['.pdf']}},
            }}],
        }});

        const pdfBlob = new Blob([new Uint8Array(atob("{pdf_base64}").split("").map(c => c.charCodeAt(0)))], {{
            type: 'application/pdf'
        }});

        const writableStream = await handle.createWritable();
        await writableStream.write(pdfBlob);
        await writableStream.close();
    }}

    document.getElementById("picker").onclick = run;
    </script>
    """
    components.html(js, height=100)

# Main function to process the assistant response and generate the PDF
def process_assistant_response(assistant_response):
    try:
        logger.debug("Processing assistant response.")
        # Parse JSON response
        if assistant_response.startswith("```json") and assistant_response.endswith("```"):
            assistant_response = assistant_response[7:-3].strip()
        sections = json.loads(assistant_response)

        # Preprocess data
        sections = preprocess_json(sections)

        # Generate LaTeX content
        rendered_latex = render_latex_template(sections)
        
        # Write LaTeX content to .tex file
        tex_filename = "generated_resume.tex"
        logger.debug(f"Writing LaTeX content to {tex_filename}.")
        with open(tex_filename, 'w', encoding='utf-8') as f:
            f.write(rendered_latex)

        # Set your specific folder path here
        output_dir = r"C:\Users\sumit\OneDrive\Desktop\Ankit POC\Outputs"  # Use raw string literal

        # Compile LaTeX to PDF and save it in the specified folder
        pdf_file = compile_latex_to_pdf(tex_filename, output_dir)
        prepare_pdf_for_download(pdf_file)
        
    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse JSON: {e}")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
