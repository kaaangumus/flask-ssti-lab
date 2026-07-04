# syntax=docker/dockerfile:1
FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    FLAG_PATH=/app/flag.txt

WORKDIR /app

RUN addgroup --system lab && adduser --system --ingroup lab lab

COPY requirements.txt .
RUN python -m pip install --no-cache-dir -r requirements.txt

COPY --chown=lab:lab . .

ARG FLAG="LAB{TEMPLATE_CONTEXT_DISCOVERED}"
RUN printf "%s" "$FLAG" > "$FLAG_PATH" && chown lab:lab "$FLAG_PATH"

USER lab
EXPOSE 5000

HEALTHCHECK --interval=30s --timeout=3s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:5000/health').read()" || exit 1

CMD ["python", "-m", "flask", "--app", "app", "run", "--host=0.0.0.0", "--port=5000"]
