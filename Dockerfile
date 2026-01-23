FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

RUN pip install gunicorn uvicorn

COPY . .

RUN useradd -m -u 1000 user
USER user

ENV HOME=/home/user \
    PATH=/home/user/.local/bin:$PATH

CMD ["gunicorn", "src.api.main:app", "--host", "0.0.0.0", "--port", "7860", "--timeout", "300", "--workers", "1", "--worker-class", "uvicorn.workers.UvicornWorker"]