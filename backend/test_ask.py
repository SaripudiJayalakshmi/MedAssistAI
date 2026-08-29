# test_ask.py
# Quick standalone script to test the RAG pipeline directly,
# so we can see the FULL error without FastAPI hiding it.

from services.vector_store import retrieve_relevant_chunks
from services.llm_service import generate_answer

question = "What are the contact details of Apollo Clinic?"

print("Step 1: Retrieving chunks...")
chunks = retrieve_relevant_chunks(question, top_k=5)
print(f"Retrieved {len(chunks)} chunks")
print(f"Top distance: {chunks[0]['similarity_distance'] if chunks else 'N/A'}")

print("\nStep 2: Generating answer with Groq...")
result = generate_answer(question, chunks)

print("\n--- RESULT ---")
print(result)