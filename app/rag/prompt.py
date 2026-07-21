from langchain_core.prompts import PromptTemplate

resume_summary_prompt = PromptTemplate.from_template(
    """
You are an experienced HR recruiter.

Resume:

{resume}

Summarize this candidate in 3 concise bullet points.

Focus on:
- Technical skills
- Experience
- Overall suitability
"""
)