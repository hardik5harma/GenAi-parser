# parser.py (Simplified with Gemini Integration)
import google.generativeai as genai

class ResumeParser:
    def __init__(self, pdf_content):
        self.pdf_content = pdf_content
        self.genai = genai
        self.genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
        self.model = self.genai.GenerativeModel('gemini-pro')
    
    def parse_resume(self):
        prompt = f"""Extract structured data from this resume:
        {self.pdf_content}
        
        Return JSON with:
        - name
        - email
        - phone
        - skills (array)
        - education (array)
        - experience (array)
        - certifications (array)
        """
        
        try:
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            return {"error": str(e)}