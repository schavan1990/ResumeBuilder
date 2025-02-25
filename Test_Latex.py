import json
import subprocess
from jinja2 import Environment, FileSystemLoader

# Define a function to escape LaTeX special characters
def escape_latex(value):
    if not value:
        return value
    # LaTeX special characters that need to be escaped
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
    # Replace all special characters with the escaped versions
    for char, replacement in latex_special_chars.items():
        value = value.replace(char, replacement)
    return value

# Preprocess JSON to escape LaTeX characters
def preprocess_json(data):
    if isinstance(data, dict):
        return {key: preprocess_json(value) for key, value in data.items()}
    elif isinstance(data, list):
        return [preprocess_json(item) for item in data]
    elif isinstance(data, str):
        return escape_latex(data)
    else:
        return data

# Process assistant response to clean and prepare JSON
def process_assistant_response(assistant_response):
    try:
        # Parse JSON and clean up headers or extraneous formatting
        if assistant_response.startswith("```json") and assistant_response.endswith("```"):
            assistant_response = assistant_response[7:-3].strip()
        # Convert the cleaned JSON string to a Python dictionary
        sections = json.loads(assistant_response)

        # Escape LaTeX special characters
        sections = preprocess_json(sections)

        # LaTeX template (using Jinja2 for dynamic rendering)
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

        # Initialize Jinja2 environment
        env = Environment(loader=FileSystemLoader('.'))
        template = env.from_string(latex_template)

        # Render LaTeX content
        rendered_latex = template.render(**sections)

        # Write to .tex file
        tex_filename = "generated_resume.tex"
        with open(tex_filename, 'w', encoding='utf-8') as f:
            f.write(rendered_latex)

        # Compile the LaTeX document using pdflatex
        try:
            subprocess.run(['pdflatex', '-interaction=nonstopmode', tex_filename], check=True)
            print("PDF generated successfully.")
        except subprocess.CalledProcessError as e:
            print(f"Error generating PDF: {e}")
        except Exception as e:
            print(f"Unexpected error: {e}")

    except json.JSONDecodeError as e:
        print(f"Failed to parse JSON: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")
