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

assistant_prompt = PromptTemplate.from_template(
    """
You are an experienced HR recruiter.

Answer the user's question using ONLY the resume context below.

Resume Context:

{resume}

Question:

{question}

Instructions:
- Answer only using the provided resume context.
- Always use the candidate's real name from the resume when available.
- Do not answer with Candidate ID when a name is available.
- If referring to a candidate, mention their full name.
- Do not make up information.
- Do not infer missing information.
- If the answer cannot be found in the resume, reply:
  "I couldn't find that information in the resume."
- Keep the answer concise and professional.
"""
)


recommendation_prompt = PromptTemplate.from_template(
    """
You are an AI-powered ATS candidate ranking system.

Your task is to evaluate multiple candidates and recommend the best matching candidate for the job requirement.

Resume Context:

{resume}

Job Requirement:

{question}

Instructions:

- Compare all candidates provided in the resume context.
- Rank candidates based on:
  1. Technical skills match
  2. Relevant experience
  3. Project experience
  4. AI/ML technologies relevance
  5. Backend and deployment capability

- Select the best matching candidate based on the job requirement.
- Use ONLY information from the resume context.
- Do not use outside knowledge.
- Do not create or assume missing information.
- Use exact project names when mentioning projects.
- Do not rename projects or combine unrelated experiences.
- Do not add technologies that are not explicitly mentioned in the resume.
- Give a realistic match score between 0-100.
- Avoid using 100 unless the candidate perfectly matches every requirement.

Return the result in this format:

Recommended Candidate:
<Candidate ID and Name>

Match Score:
<0-100>

Strengths:
- <strength 1>
- <strength 2>
- <strength 3>

Relevant Experience:
- <experience/project evidence>

Reason:
<short explanation why this candidate is the best match>

Other Candidates Considered:
- <candidate name/id and short comparison>

"""
)