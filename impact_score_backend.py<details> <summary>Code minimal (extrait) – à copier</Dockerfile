FROM python:3.11-slim

WORKDIR /app
COPY impact_score_backend.py .

RUN pip install --no-cache-dir fastapi uvicorn httpx python-dotenv openai

ENV PORT 10000
EXPOSE 10000

CMD ["uvicorn", "impact_score_backend:app", "--host", "0.0.0.0", "--port", "10000"]
