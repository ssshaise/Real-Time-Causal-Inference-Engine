FROM python:3.11

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

RUN pip install gunicorn uvicorn

COPY . .

RUN useradd -m -u 1000 user
USER user

ENV HOME=/home/user \
    PATH=/home/user/.local/bin:$PATH

CMD ["gunicorn", "src.api.main:app", "--bind", "0.0.0.0:7860", "--workers", "1", "--worker-class", "uvicorn.workers.UvicornWorker", "--timeout", "300"]