# llm_service.py
# Handles building the hybrid RAG + general-knowledge prompt and calling Llama/GPT-OSS via Groq.

import os
from dotenv import load_dotenv
from groq import Groq

load_dotenv()

client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

SYSTEM_PROMPT = """You are MedAssist AI, a helpful and responsible medical AI assistant.

Your job is to answer a wide range of medical and healthcare-related questions clearly, accurately, and safely.

You may use TWO sources of information:

1. UPLOADED MEDICAL DOCUMENTS
   - Use the provided document context whenever it is relevant to the user's question.
   - When your answer uses information from the documents, clearly indicate the relevant source.
   - Never create or invent a document citation.

2. GENERAL MEDICAL KNOWLEDGE
   - If the uploaded documents do not contain enough information to answer the question, you may use your general medical knowledge.
   - Do NOT say "I couldn't find this information in the uploaded documents" simply because the PDF does not contain the answer.
   - Clearly distinguish general medical knowledge from information obtained from the uploaded documents.

ANSWERING RULES:

- Answer the user's medical question directly and naturally.
- You can answer questions even when they are unrelated to the uploaded documents.
- Provide clear explanations using simple language.
- For complex topics, organize the answer using headings and bullet points.
- Explain symptoms, possible causes, diagnosis, treatment options, prevention, and when to seek medical care when relevant.
- Do not diagnose the user with certainty based only on their message.
- Do not prescribe personalized medication doses or treatment plans without appropriate clinical evaluation.
- For urgent or emergency symptoms, advise the user to seek immediate professional medical attention.
- If the question is ambiguous, ask a short clarifying question when necessary.
- Never fabricate medical facts, sources, studies, or citations.
- Do not claim that information came from the uploaded documents unless it actually came from the provided context.

SOURCE LABELING:

If the answer is based on the uploaded documents:
"Source: Uploaded medical document"

If the answer is based primarily on general medical knowledge:
"Source: General medical knowledge"

If both are used:
"Sources: Uploaded medical document + General medical knowledge"

SAFETY DISCLAIMER:

For medical advice that could affect a person's health or treatment, include a brief reminder such as:

"This information is for educational purposes and does not replace advice from a qualified healthcare professional."

Your goal is to be useful, accurate, transparent about your sources, and medically safe."""

# Chunks with a distance BELOW this are considered genuinely relevant and get
# included as grounding context. Chunks above it are treated as "not relevant" -
# we don't include them, but we no longer refuse to answer outright.
DISTANCE_THRESHOLD = 1.0


def build_context(relevant_chunks: list[dict]) -> str:
    """Formats only the genuinely relevant chunks into a labeled context block."""
    context_parts = []
    for chunk in relevant_chunks:
        source = chunk["source_document"]
        text = chunk["text"]
        context_parts.append(f"[Source: {source}]\n{text}")
    return "\n\n---\n\n".join(context_parts)


def generate_answer(question: str, retrieved_chunks: list[dict]) -> dict:
    """
    Hybrid RAG + general-knowledge generation:
    - Chunks below the distance threshold are passed in as grounding context.
    - The LLM is instructed to use them when relevant, and fall back to its own
      medical knowledge otherwise - always labeling which source it used.
    """
    relevant_chunks = [
        c for c in retrieved_chunks if c["similarity_distance"] <= DISTANCE_THRESHOLD
    ]

    if relevant_chunks:
        context = build_context(relevant_chunks)
        user_message = f"""Context from uploaded medical documents (use if relevant):
{context}

Question: {question}

Answer using the document context above if it's relevant to the question.
If the documents don't fully answer it, use your general medical knowledge to complete
the answer, and clearly label your sources as instructed."""
    else:
        # No relevant document chunks - let the model answer from general knowledge,
        # but be explicit that no document context was found, so it doesn't invent a citation.
        user_message = f"""No relevant content was found in the uploaded medical documents for this question.

Question: {question}

Answer using your general medical knowledge. Label the source as
"Source: General medical knowledge" and do not reference any document."""

    response = client.chat.completions.create(
        model="openai/gpt-oss-120b",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_message},
        ],
        temperature=0.3,
    )

    answer_text = response.choices[0].message.content

    # Only report sources that were ACTUALLY used as grounding context -
    # never claim a document was used if it wasn't included above the threshold.
    sources = list({c["source_document"] for c in relevant_chunks})

    return {
        "answer": answer_text,
        "sources": sources,
    }