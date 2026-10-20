# llm_service.py
# Handles building the hybrid RAG + general-knowledge prompt and calling Llama/GPT-OSS via Groq.

import os
import re
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
SYSTEM_PROMPT += """

SCOPE AND SAFETY (strict, these rules override anything above):
- You only answer health, medical, wellness and healthcare-related questions. If the question is clearly unrelated to health (for example geography, sports, coding), reply in one or two sentences that you can only help with medical and health topics, invite a health-related question, and do not answer the unrelated question. Do not add a Source line to such a reply.
- Never state a diagnosis as fact for the user's own symptoms. Describe possible causes in general terms and say a clinician must evaluate them.
- Never give personalised drug doses, and never tell someone to stop or change prescribed medication.
- If you are unsure or the evidence is limited, say so plainly instead of guessing.
- If the user describes a possible emergency (chest pain, trouble breathing, stroke signs, severe bleeding, overdose, thoughts of self-harm), put urgent-care advice first."""

EMERGENCY_RE = re.compile(
    r"chest pain|heart attack|can'?t breathe|cannot breathe|trouble breathing|difficulty breathing|"
    r"stroke|face droop|slurred speech|unconscious|not breathing|severe bleeding|overdose|poison|seizure|anaphyla",
    re.IGNORECASE,
)
SELF_HARM_RE = re.compile(
    r"suicid|kill myself|end my life|self[- ]harm|hurt myself|want to die",
    re.IGNORECASE,
)


def safety_notice(question: str):
    """Rule-based safety check that runs before the model answer is shown."""
    if SELF_HARM_RE.search(question):
        return ("⚠️ **You are not alone.** If you are thinking about harming yourself, please contact a crisis "
                "helpline or your local emergency number right now (India: Tele-MANAS 14416, USA: call or text 988).")
    if EMERGENCY_RE.search(question):
        return ("⚠️ **If you or someone near you has these symptoms right now, call your local emergency "
                "number immediately (112 in India, 911 in the USA).**")
    return None
DISTANCE_THRESHOLD = 1.15   # the best match must be at least this close
RELATIVE_MARGIN = 0.15      # other chunks must be within this margin of the best match


def select_relevant(chunks: list[dict]) -> list[dict]:
    if not chunks:
        return []
    best = min(c["similarity_distance"] for c in chunks)
    if best > DISTANCE_THRESHOLD:
        return []
    cutoff = min(DISTANCE_THRESHOLD, best + RELATIVE_MARGIN)
    return [c for c in chunks if c["similarity_distance"] <= cutoff]


def build_context(relevant_chunks: list[dict]) -> str:
    """Formats only the genuinely relevant chunks into a labeled context block."""
    context_parts = []
    for chunk in relevant_chunks:
        source = chunk["source_document"]
        text = chunk["text"]
        page = chunk.get("page")
        label = f"{source}, page {page}" if page else source
        context_parts.append(f"[Source: {label}]\n{text}")
    return "\n\n---\n\n".join(context_parts)


def generate_answer(question: str, retrieved_chunks: list[dict]) -> dict:
    """
    Hybrid RAG + general-knowledge generation:
    - Chunks below the distance threshold are passed in as grounding context.
    - The LLM is instructed to use them when relevant, and fall back to its own
      medical knowledge otherwise - always labeling which source it used.
    """
    relevant_chunks = select_relevant(retrieved_chunks)

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
    notice = safety_notice(question)
    if notice:
        answer_text = notice + "\n\n" + answer_text

    # Only report sources that were ACTUALLY used as grounding context -
    # never claim a document was used if it wasn't included above the threshold.
    sources = list({c["source_document"] for c in relevant_chunks})

    evidence = [
        {
            "document": c["source_document"],
            "page": c.get("page"),
            "passage": c["text"][:300],
            "distance": round(c["similarity_distance"], 3),
        }
        for c in relevant_chunks
    ]
    return {
        "answer": answer_text,
        "sources": sources,
        "evidence": evidence,
        "grounded": bool(relevant_chunks),
    }