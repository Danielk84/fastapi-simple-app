FROM python:3.13-slim

WORKDIR /app

COPY . .

RUN pip install poetry

RUN poetry install --no-root

EXPOSE 8000

CMD ["poetry", "run", "fastapi", "dev", "--host", "0.0.0.0", "--port", "8000", "app"]