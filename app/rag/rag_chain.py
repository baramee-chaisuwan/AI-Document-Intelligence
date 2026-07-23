from langchain_core.output_parsers import StrOutputParser

from app.rag.chain import llm
from app.rag.prompt import resume_summary_prompt as prompt
from app.vector.vector_service import search_documents


def ask_rag(question: str):

    results = search_documents(
        query=question,
        n_results=3
    )

    context = "\n\n".join(
        results["documents"][0]
    )

    chain = (
        prompt
        | llm
        | StrOutputParser()
    )

    answer = chain.invoke(
        {
            "resume": context,
            "question": question
        }
    )

    return answer