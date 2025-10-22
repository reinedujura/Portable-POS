import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI

load_dotenv()

api_key = os.getenv("GOOGLE_API_KEY")
model = os.getenv("GEMINI_MODEL")

if not api_key:
    raise ValueError("GOOGLE_API_KEY environment variable is not set.")

llm = ChatGoogleGenerativeAI(
    model=model, 
    api_key=api_key,
    temperature=0.2,
)