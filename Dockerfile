# Dockerfile (place at the root of agentwebplus/)
FROM python:3.11-slim
 
WORKDIR /app
COPY . /app
 
# Optional: build tools for psycopg (safe to include)
RUN apt-get update && apt-get install -y build-essential && rm -rf /var/lib/apt/lists/*
 
RUN pip install --no-cache-dir -r requirements.txt
 
ENV PYTHONPATH=/app
ENV PORT=8501
EXPOSE 8501
 
# Use ${PORT} if provided by the platform (Render), else 8501 locally
CMD ["bash", "-lc", "streamlit run app/streamlit_ui.py --server.port ${PORT:-8501} --server.address 0.0.0.0"]
 