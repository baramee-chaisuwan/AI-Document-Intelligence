from app.rag.chain import resume_summary_chain


def summarize_resume_with_langchain(
    resume_text: str
):

    response = resume_summary_chain.invoke(
        {
            "resume": resume_text
        }
    )

    return response.content