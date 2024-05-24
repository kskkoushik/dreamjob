import base64
import os
import io
import pdf2image
from docx import Document
from io import BytesIO
import google.generativeai as genai
from dotenv import load_dotenv
import requests
from flask import Flask, render_template, request
import PyPDF2

# Load environment variables
load_dotenv()

app = Flask(__name__)

# Configure generativeai with API key 
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

def format_response(response):
    # Replace newline characters with <br> tags for line breaks
    formatted_response = response.replace('\n', '<br>')
    return formatted_response

def input_pdf_setup(uploaded_file):
    pdf_reader = PyPDF2.PdfReader(uploaded_file)
    text = ''
    for page_num in range(len(pdf_reader.pages)):
        page = pdf_reader.pages[page_num]
        text += page.extract_text()
    return text

def get_gemini_response(input, pdf_content, prompt):
    model = genai.GenerativeModel('gemini-pro')
    response = model.generate_content([input, pdf_content, prompt])
    return format_response(response.text)

@app.route('/', methods=['GET', 'POST'])
def unified_route():
    if request.method == 'GET':
        return render_template('index.html')
    else:
        input_text = request.form['job_description']
        uploaded_file = request.files['pdf_file']
        feature = request.form['feature']

        pdf_content = input_pdf_setup(uploaded_file)

        if feature == 'resume_eval':
            input_prompt = """
            You are an experienced Technical Human Resource Manager, your task is to review the provided resume against the job description.
            Please share your professional evaluation on whether the candidate's profile aligns with the role.
            Highlight the major things:
            1. Formatting and Presentation (Weight: 10%)
            2. Key Skills and Achievements (Weight: 30%)
            3. Work Experience Alignment (Weight: 40%)
            4. Bonus: Keyword Match (Weight: 20%)
            And tell how is he/she good for that company.
            """
        elif feature == 'analyze_cv':
            input_prompt = """
            You are an expert CV reviewer. Review the CV and provide:
            1. Strengths
            2. Weaknesses
            Mention where the applicant can improve themselves according to the CV as bullet points.
            """
        elif feature == 'job_prep':
            input_prompt = """
            You are a skilled and experienced professional in your field, currently preparing for a job interview.
            Your goal is to generate relevant interview questions and answers based on your job description.
            Please provide details about your professional background, skills, and experiences.
            Mention key areas that align with the job description to receive customized interview questions.
            """
        elif feature == 'interview_sim':
            input_prompt = """
            You are a seasoned interviewer conducting an interview for the position of [Job Title].
            Generate 15 interview questions and provide expert-level answers to help job seekers prepare for interviews.
            """
        elif feature == 'cover_letter':
            input_prompt = """
            You are a skilled Cover Letter Writer. Your task is to write a powerful cover letter based on the provided CV and job description.
            Consider tailoring the cover letter to the specific company and highlighting:
            1. The candidate's relevant skills and experiences mentioned from the CV.
            2. How the candidate is helpful for this position.
            3. How passionate the candidate is for the job.
            Lastly, mention the candidate's name, address, phone number, and email address collected from the CV.
            """
        elif feature == 'recruiter_mail':
            input_prompt = """
            You are a skilled Email Writer to a recruiter. Your task is to write a short and powerful email with a strong subject line to the recruiter based on the provided CV and job description.
            Consider tailoring the email to the specific company and highlighting:
            1. Between 50 to 125 words.
            2. The candidate's relevant skills and experiences mentioned from the CV.
            3. How the candidate is helpful for this position.
            4. How passionate the candidate is for the job.
            Lastly, mention the candidate's name, address, phone number, and email address collected from the CV. Note that the email should be short and powerful.
            """
        elif feature == 'career_suggestion':
            input_prompt = """
            You are a specialist career advisor and planner providing personalized recommendations based on the user's CV.
            Analyze the uploaded CV and suggest potential career paths, future scope, skill development areas, and job opportunities as bullet points highlighting major points.
            """

        response = get_gemini_response(input_text, pdf_content, input_prompt)
        print(response)
        return render_template('index.html', result=response)

if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=True)
