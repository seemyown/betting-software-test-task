FROM python:3.10-slim
ENV PYTHONUNBUFFERED=1
ENV TZ="Europe/Moscow"

RUN mkdir /app
RUN pip install poetry

WORKDIR /app

RUN poetry --version

COPY . .

RUN poetry config virtualenvs.create false

RUN poetry install --no-root --only main

EXPOSE 8000

CMD ["fastapi", "run", "--host", "0.0.0.0", "--port", "8000", "--proxy-headers"]