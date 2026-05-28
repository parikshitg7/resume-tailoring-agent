import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from schemas import JDAnalysis

# Load the API Key from the .env file
load_dotenv()

# Initialize the Groq model using Llama 3 70B
llm = ChatGroq(
    model="llama-3.3-70b-versatile",
    api_key=os.getenv("GROQ_API_KEY"),
    temperature=0.1 # Low temperature means more factual, precise extraction
)

# Bind the Pydantic schema to force the AI to return clean JSON matching our model
structured_analyzer = llm.with_structured_output(JDAnalysis)

def analyze_job_description(jd_text: str) -> JDAnalysis:
    """
    Sends raw Job Description text to Groq and extracts a structured analytical layout.
    """
    prompt = f"Analyze the following job description thoroughly. Extract the required skills, experience level, responsibilities, and key ATS optimization keywords:\n\n{jd_text}"
    
    # Groq processes the text instantly and returns a JDAnalysis Pydantic object
    analysis_result = structured_analyzer.invoke(prompt)
    return analysis_result