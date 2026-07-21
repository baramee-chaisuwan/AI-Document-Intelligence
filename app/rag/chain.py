from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI

from app.rag.prompt import resume_summary_prompt

load_dotenv()

llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    temperature=0
)

resume_summary_chain = resume_summary_prompt | llm