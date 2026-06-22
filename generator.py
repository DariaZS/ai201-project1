"""
generator.py
Connects retrieval to Groq LLM with strict grounding.
The system prompt enforces answers from retrieved context only.
"""

import os

from dotenv import load_dotenv
from groq import Groq

from retriever import embed_and_store, query

load_dotenv()

client = Groq(api_key=os.environ.get("GROQ_API_KEY"))
MODEL = "llama-3.3-70b-versatile"

SYSTEM_PROMPT = """You are a helpful assistant for Columbia University students.
Answer questions using ONLY the information provided in the context below.
Do not use any outside knowledge, even if you are confident about it.
If the provided context does not contain enough information to answer the question,
respond with exactly: "I don't have enough information on that in my documents."
Always cite which source document(s) your answer came from."""


def ask(question: str) -> dict:
    """
    Full RAG pipeline: retrieve relevant chunks, generate grounded answer.
    Returns {"answer": str, "sources": list[str]}
    """
    # Step 1: Retrieve relevant chunks
    chunks = query(question)

    # Step 2: Build context string from retrieved chunks
    context_parts = []
    for i, chunk in enumerate(chunks, 1):
        context_parts.append(
            f"[Document {i} - source: {chunk['source']}]\n{chunk['text']}"
        )
    context = "\n\n".join(context_parts)

    # Step 3: Build the user message with context + question
    user_message = f"""Context:
{context}

Question: {question}

Answer using only the context above. Cite the source document name(s) in your answer."""

    # Step 4: Call Groq LLM
    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_message},
        ],
        temperature=0.2,  # low temperature for factual, consistent answers
    )

    answer = response.choices[0].message.content

    # Step 5: Collect unique source names for programmatic attribution
    sources = list(dict.fromkeys(chunk["source"] for chunk in chunks))

    return {"answer": answer, "sources": sources}


if __name__ == "__main__":
    # Make sure vector store is populated
    embed_and_store()

    # Test with 3 queries including one the docs don't cover
    test_questions = [
        "How does the Columbia housing lottery actually work?",
        "How do I register for disability accommodations at Columbia?",
        "What GPA do I need to get into Harvard Law School?",  
        "What CS courses should I take first as a Columbia CS major?",
        "What do students recommend for cheap food near Columbia?",
    ]

    for q in test_questions:
        print(f"\nQ: {q}")
        print("-" * 60)
        result = ask(q)
        print(f"A: {result['answer']}")
        print(f"\nSources: {', '.join(result['sources'])}")
        print()