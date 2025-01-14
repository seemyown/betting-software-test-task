FROM python:3.10-slim
ENV PYTHONUNBUFFERED=1
ENV TZ="Europe/Moscow"

RUN mkdir /provider
RUN pip install poetry

WORKDIR /provider

RUN poetry --version

COPY . .

RUN poetry config virtualenvs.create false

RUN poetry install --no-root --only main

CMD ["python3", "app/main.py"]