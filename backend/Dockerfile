FROM tiangolo/uvicorn-gunicorn-fastapi:python3.11-slim

LABEL maintainer="Max Mecklin <max@meckl.in>"

COPY . /app

WORKDIR /app

RUN date +%Y.%m.%d > .build

ENV PYTHONPATH "${PYTHONPATH}:/app"
ENV VERSION=${BUILD_VERSION}

RUN pip install -r requirements.txt