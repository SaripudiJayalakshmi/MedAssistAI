# llm_service.py
# Handles building the RAG prompt and calling Llama 3 via Groq.

import os
from dotenv import load_dotenv
from groq import Groq

load_dotenv()  # reads .env and loads GROQ_API_KEY into environment variables

client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

# The exact system prompt from your spec — enforces "only answer from context"
SYSTEM_PROMPT = """You are an expert medical AI assistant.

Only answer using the retrieved medical context.
Never generate information that is not found in the provided documents.
If the answer is unavailable, respond exactly:
'I couldn't find this information in the uploaded medical documents.'

Always cite the source document for any claim you make.
Keep answers clear and structured. Include a short medical disclaimer at the end
reminding the user this is not a substitute for professional medical advice."""

# If the closest chunk's distance is above this, we consider it "not relevant enough"
DISTANCE_THRESHOLD = 1.0


def build_context(retrieved_chunks: list[dict]) -> str:
    """
    Formats retrieved chunks into a single text block the LLM can read,
    labeling each with its source so the model can cite it correctly.
    """
    context_parts = []
    for chunk in retrieved_chunks:
        source = chunk["source_document"]
        text = chunk["text"]
        context_parts.append(f"[Source: {source}]\n{text}")

    return "\n\n---\n\n".join(context_parts)


def generate_answer(question: str, retrieved_chunks: list[dict]) -> dict:
    """
    Full RAG generation step: checks if retrieval was relevant enough,
    builds a prompt, calls Groq's Llama 3, and returns the answer.
    """
    # Guard clause: if nothing was retrieved, or the best match is too far off,
    # don't even bother calling the LLM — save cost and avoid hallucination risk
    if not retrieved_chunks or retrieved_chunks[0]["similarity_distance"] > DISTANCE_THRESHOLD:
        return {
            "answer": "I couldn't find this information in the available medical documents.",
            "sources": [],
        }

    context = build_context(retrieved_chunks)

    # Build the actual message sent to the LLM
    user_message = f"""Context from medical documents:
{context}

Question: {question}

Answer the question using ONLY the context above."""

    response = client.chat.completions.create(
        model="openai/gpt-oss-120b",  # current Groq-hosted Llama 3 model
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_message},
        ],
        temperature=0.2,  # low temperature = more focused/deterministic, less "creative"
    )

    answer_text = response.choices[0].message.content

    # Collect unique source documents used, for a clean citation list
    sources = list({chunk["source_document"] for chunk in retrieved_chunks})

    return {
        "answer": answer_text,
        "sources": sources,
    }