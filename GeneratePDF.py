import json
import os
import logging
import streamlit as st
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Table, TableStyle, ListFlowable, ListItem
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from io import BytesIO
import base64

# Set up logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def create_custom_styles():
    """Create custom styles for the PDF document"""
    styles = getSampleStyleSheet()
    
    # Header style
    styles.add(ParagraphStyle(
        name='CustomHeader',
        parent=styles['Heading2'],
        fontSize=16,
        spaceAfter=20,
        alignment=1  # Center alignment
    ))
    
    # Contact info style
    styles.add(ParagraphStyle(
        name='ContactInfo',
        parent=styles['Normal'],
        fontSize=10,
        alignment=1,
        spaceAfter=15
    ))
    
    # Section header style
    styles.add(ParagraphStyle(
        name='SectionHeader',
        parent=styles['Heading2'],
        fontSize=12,
        spaceBefore=15,
        spaceAfter=10
    ))
    
    # Experience header style
    styles.add(ParagraphStyle(
        name='ExperienceHeader',
        parent=styles['Normal'],
        fontSize=11,
        spaceBefore=10,
        spaceAfter=5,
        fontName='Helvetica-Bold'
    ))
    
    return styles

def generate_pdf(resume_data):
    """Generate PDF using ReportLab"""
    try:
        buffer = BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=letter,
            rightMargin=0.15*inch,
            leftMargin=0.15*inch,
            topMargin=0.15*inch,
            bottomMargin=0.15*inch
        )
        
        styles = create_custom_styles()
        story = []
        
        # Contact Information
        contact = resume_data['contactInformation']
        story.append(Paragraph(contact['name'], styles['CustomHeader']))
        contact_text = f"{contact['location']}<br/>{contact['email']}"
        if contact.get('phone'):
            contact_text += f" | {contact['phone']}"
        if contact.get('linkedin'):
            contact_text += f"<br/>{contact['linkedin']}"
        story.append(Paragraph(contact_text, styles['ContactInfo']))
        
        # Professional Summary
        if 'professionalSummary' in resume_data:
            story.append(Paragraph(resume_data['professionalSummary'], styles['Normal']))
        
        # Professional Experience
        story.append(Paragraph("Work Experience", styles['Heading2']))
        for exp in resume_data['professionalExperience']:
            header_text = (
                f"<b>{exp['company']}</b> - {exp['role']}"
                f"<br/><i>{exp['location']} | {exp['date']}</i>"
            )
            story.append(Paragraph(header_text, styles['ExperienceHeader']))
            
            # Achievements
            achievements = []
            for achievement in exp['achievements']:
                achievements.append(
                    ListItem(Paragraph(achievement, styles['Normal']))
                )
            story.append(ListFlowable(
                achievements,
                bulletType='bullet',
                leftIndent=20,
                spaceBefore=5,
                spaceAfter=10
            ))
        
        # Education
        story.append(Paragraph("Education", styles['Heading2']))
        for edu in resume_data['education']:
            header_text = (
                f"<b>{edu['institution']}</b> - {edu['degree']}"
                f"<br/><i>{edu.get('location', '')} | {edu['date']}</i>"
            )
            story.append(Paragraph(header_text, styles['ExperienceHeader']))
            
            # if edu.get('achievements'):
            #     achievements = []
            #     for achievement in edu['achievements']:
            #         achievements.append(
            #             ListItem(Paragraph(achievement, styles['Normal']))
            #         )
            #     story.append(ListFlowable(
            #         achievements,
            #         bulletType='bullet',
            #         leftIndent=20,
            #         spaceBefore=5,
            #         spaceAfter=10
            #     ))

        # Certifications
        story.append(Paragraph("Certifications", styles['Heading2']))
        for cert in resume_data['certifications']:
            cert_text = (
                f"<b>{cert['name']}</b> - {cert['organization']}"
            )
            story.append(Paragraph(cert_text, styles['ExperienceHeader']))
        
        # Awards and Projects
        story.append(Paragraph("Awards & Projects", styles['Heading2']))
        for project in resume_data['awardsAndProjects']:
            project_text = (
                f"<b>{project['project']}</b> - {project['organization']}"
            )
            story.append(Paragraph(project_text, styles['ExperienceHeader']))
            
            if project.get('achievements'):
                achievements = []
                for achievement in project['achievements']:
                    achievements.append(
                        ListItem(Paragraph(achievement, styles['Normal']))
                    )
                story.append(ListFlowable(
                    achievements,
                    bulletType='bullet',
                    leftIndent=20,
                    spaceBefore=5,
                    spaceAfter=10
                ))

        # Skills (Multi-Column Bullet Points)
        story.append(Paragraph("Skills", styles['Heading2']))
        skills = resume_data.get('skills', [])

        if skills:
            # Split skills into 4 columns
            columns = 4
            column_height = len(skills) // columns + (len(skills) % columns > 0)
            columns_data = [skills[i:i + column_height] for i in range(0, len(skills), column_height)]
            
            # Create ListFlowables for each column
            list_items = []
            for column in columns_data:
                bullet_list = []
                for skill in column:
                    bullet_list.append(Paragraph(f"• {skill}", styles['Normal']))  # Use Paragraph instead of ListItem
                list_items.append(bullet_list)
            
            # Add them to the story, side by side
            for i in range(column_height):
                line = []
                for j in range(columns):
                    if i < len(list_items[j]):  # Check if the column has enough items
                        line.append(list_items[j][i])
                if line:  # Only add the line if it's not empty
                    # Join the text of each line element properly and add to the story
                    line_text = "".join([str(item.getPlainText()) for item in line])  # Ensure we extract plain text only
                    story.append(Paragraph(line_text, styles['Normal']))

        else:
            story.append(Paragraph("No skills available", styles['Normal']))


        doc.build(story)
        return buffer.getvalue()
        
    except Exception as e:
        logger.error(f"Error generating PDF: {str(e)}")
        raise

def create_download_button(pdf_data):
    """Create a download button for the PDF"""
    try:
        b64_pdf = base64.b64encode(pdf_data).decode()
        
        custom_css = """
            <style>
                .download-button {
                    background-color: #4CAF50;
                    color: white;
                    padding: 10px 20px;
                    border: none;
                    border-radius: 4px;
                    cursor: pointer;
                    font-size: 16px;
                    transition: background-color 0.3s;
                }
                .download-button:hover {
                    background-color: #45a049;
                }
            </style>
        """
        
        download_button = f"""
            {custom_css}
            <button class="download-button" onclick="downloadPDF()">
                📄 Download Resume PDF
            </button>
            
            <script>
                function downloadPDF() {{
                    try {{
                        const b64Data = "{b64_pdf}"; 
                        const blob = new Blob(
                            [Uint8Array.from(atob(b64Data), c => c.charCodeAt(0))],
                            {{type: 'application/pdf'}}
                        );
                        const url = window.URL.createObjectURL(blob);
                        const link = document.createElement('a');
                        link.href = url;
                        link.download = 'resume.pdf';
                        document.body.appendChild(link);
                        link.click();
                        window.URL.revokeObjectURL(url);
                        document.body.removeChild(link);
                    }} catch(error) {{
                        console.error("Download failed:", error);
                        alert("Download failed. Please try again.");
                    }}
                }}
            </script>
        """
        
        st.components.v1.html(download_button, height=70)
        
    except Exception as e:
        logger.error(f"Error creating download button: {str(e)}")
        st.error("Error creating download button. Please try again.")

def process_assistant_response(assistant_response):
    """Process the assistant response and generate PDF"""
    try:
        # Check if assistant response is a valid JSON string
          # Show the assistant response for tracking
        #st.write("Assistant Response:", assistant_response)
        if isinstance(assistant_response, str):
            logger.debug("Assistant response is a string, attempting to parse JSON.")
            if assistant_response.startswith("```json") and assistant_response.endswith("```"):
                assistant_response = assistant_response[7:-3].strip()
        
        # Try to load JSON
        try:
            resume_data = json.loads(assistant_response)
            logger.debug("Successfully parsed JSON.")
        except json.JSONDecodeError as e:
            logger.error(f"JSON parsing error: {str(e)}. Response: {assistant_response}")
            st.error(f"❌ Error parsing resume data: {str(e)}. Please ensure valid JSON format.")
            return

        # Validate required sections
        required_sections = ['contactInformation', 'professionalExperience', 'education']
        missing_sections = [section for section in required_sections if section not in resume_data]
        if missing_sections:
            logger.error(f"Missing required sections: {', '.join(missing_sections)}")
            st.error(f"❌ Missing required sections: {', '.join(missing_sections)}")
            return
        
        # Generate PDF
        pdf_data = generate_pdf(resume_data)
        
        if pdf_data:
            st.success("✅ PDF generated successfully!")
            create_download_button(pdf_data)
        else:
            st.error("❌ Failed to generate PDF. Please check the logs for details.")
            
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        st.error(f"❌ An unexpected error occurred: {str(e)}")
