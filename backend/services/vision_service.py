import os, base64
from dotenv import load_dotenv
from groq import Groq

load_dotenv()
_client = Groq(api_key=os.environ["GROQ_API_KEY"])
VISION_MODEL = "qwen/qwen3.8-27b"
SYSTEM = ("You are MedAssist AI. Explain the medical image in educational terms. "
          "Do not give a definitive diagnosis, state uncertainty, and advise consulting a qualified clinician. "
          "If the image is not medically relevant, say so briefly.")

def ask_about_image(image_bytes, mime, question):
    b64 = base64.b64encode(image_bytes).decode()
    q = (question or "").strip() or "Describe this image and any medically relevant findings."
    r = _client.chat.completions.create(
        model=VISION_MODEL, temperature=0.3, max_tokens=800,
        messages=[{"role": "system", "content": SYSTEM},
                  {"role": "user", "content": [
                      {"type": "text", "text": q},
                      {"type": "image_url", "image_url": {"url": f"data:{mime};base64,{b64}"}}]}])
    return r.choices[0].message.content