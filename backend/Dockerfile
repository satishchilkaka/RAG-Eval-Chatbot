FROM python:3.12-slim-bookworm

WORKDIR /app/backend

COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Pre-download lightweight ONNX embedding model (~80 MB vs ~2 GB for PyTorch)
RUN python -c "from chromadb.utils.embedding_functions import ONNXMiniLM_L6_V2; ONNXMiniLM_L6_V2()"

COPY backend/app ./app

ENV PYTHONUNBUFFERED=1
ENV ANONYMIZED_TELEMETRY=False

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
