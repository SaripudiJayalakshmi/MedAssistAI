FROM python:3.11-slim
RUN useradd -m -u 1000 user
WORKDIR /home/user/app
COPY --chown=user . .
ENV HOME=/home/user PATH=/home/user/.local/bin:$PATH
USER user
RUN pip install --no-cache-dir -r requirements.txt
RUN python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('all-MiniLM-L6-v2')"
RUN mkdir -p uploads chroma_db
EXPOSE 7860
CMD ["uvicorn","main:app","--host","0.0.0.0","--port","7860"]
