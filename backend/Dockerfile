
FROM python:3.11-slim

RUN useradd -m -u 1000 user

WORKDIR /home/user/app

COPY --chown=user:user . .

ENV HOME=/home/user
ENV PATH=/home/user/.local/bin:$PATH
ENV SENTENCE_TRANSFORMERS_HOME=/home/user/.cache/torch/sentence_transformers
ENV HF_HOME=/home/user/.cache/huggingface

RUN pip install --no-cache-dir -r requirements.txt \
    && mkdir -p uploads chroma_db /home/user/.cache \
    && chown -R user:user /home/user

USER user

RUN python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('all-MiniLM-L6-v2')"

EXPOSE 7860

CMD ["sh", "-c", "uvicorn main:app --host 0.0.0.0 --port ${PORT:-7860}"]
