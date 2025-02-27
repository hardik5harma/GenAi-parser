# app.py (Updated with Gemini AI Integration)

###### Packages Used ######
import streamlit as st
import os
import google.generativeai as genai
from PIL import Image
import base64
import pymongo
import time
import datetime

# Configure Gemini API
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))  # Use environment variable for security
model = genai.GenerativeModel('gemini-pro')

###### MongoDB Connection ######
client = pymongo.MongoClient(os.getenv("MONGODB_ATLAS_URI"))
db = client.skillpathai
users_col = db.users
courses_col = db.courses

###### Helper Functions ######
def get_pdf_text(uploaded_file):
    """Extract text from PDF using Gemini"""
    try:
        pdf_bytes = uploaded_file.getvalue()
        response = model.generate_content(
            f"Extract text from this PDF file: {pdf_bytes}",
            request_options={"timeout": 600}
        )
        return response.text
    except Exception as e:
        st.error(f"Error extracting text: {str(e)}")
        return ""

def analyze_resume(text):
    """Analyze resume text with Gemini"""
    prompt = f"""Analyze this resume text and extract:
    - Name
    - Email
    - Phone number
    - Technical skills
    - Education degrees
    - Work experience
    - Certifications
    
    Return in JSON format. Resume text: {text}"""
    
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        st.error(f"Analysis failed: {str(e)}")
        return None

def generate_recommendations(skills, goals):
    """Generate learning recommendations using Gemini"""
    prompt = f"""Create a learning path for someone with skills: {skills} 
    who wants to achieve: {goals}. Recommend 5 technical skills to develop 
    and 3 LinkedIn Learning courses for each skill. Return as JSON with fields:
    - recommended_skills (array)
    - courses (array of objects with skill, course_title, reason)"""
    
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        st.error(f"Recommendation failed: {str(e)}")
        return None

###### Streamlit UI ######
def main():
    st.set_page_config(page_title="SkillPath AI", page_icon="🚀")
    
    st.title("SkillPath AI - Career Growth Assistant")
    st.write("Upload your resume and set your career goals for personalized learning recommendations")
    
    # User Input Section
    with st.form("user_input"):
        uploaded_file = st.file_uploader("Upload Resume (PDF)", type="pdf")
        career_goal = st.text_input("Career Goal (e.g., 'Become a Data Scientist')")
        submitted = st.form_submit_button("Analyze & Recommend")
    
    if submitted and uploaded_file:
        with st.spinner("Analyzing your profile..."):
            # Process PDF
            resume_text = get_pdf_text(uploaded_file)
            
            # Analyze with Gemini
            analysis = analyze_resume(resume_text)
            
            if analysis:
                # Generate Recommendations
                recommendations = generate_recommendations(
                    skills=analysis.get('skills', []),
                    goals=career_goal
                )
                
                # Store in MongoDB
                user_data = {
                    "timestamp": datetime.datetime.now(),
                    "analysis": analysis,
                    "recommendations": recommendations,
                    "progress": []
                }
                users_col.insert_one(user_data)
                
                # Display Results
                st.subheader("Your Career Development Plan")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown("### Current Skills")
                    st.write(", ".join(analysis.get('skills', [])))
                    
                with col2:
                    st.markdown("### Recommended Skills")
                    for skill in recommendations.get('recommended_skills', []):
                        st.markdown(f"- {skill}")
                
                st.markdown("### Recommended Courses")
                for course in recommendations.get('courses', []):
                    with st.expander(f"{course['skill']}: {course['course_title']}"):
                        st.write(course['reason'])
                        if st.button("Mark as Completed", key=course['course_title']):
                            users_col.update_one(
                                {"_id": user_data["_id"]},
                                {"$push": {"progress": course['course_title']}}
                            )
                            st.success("Course marked as completed!")

if __name__ == "__main__":
    main()