FROM python:3.11-slim-bookworm

WORKDIR /opt

ENV PYTHONUNBUFFERED=1 PYTHONPATH="$PYTHONPATH:/opt:/opt/src"


COPY requirements.txt ./requirements.txt
COPY entrypoint.sh ./entrypoint.sh

RUN apt-get update  \
    && apt-get install -y gcc  \
    && apt install netcat-traditional

RUN groupadd -r app  \
    && useradd -d /opt -r -g app app \
    && mkdir -p /opt/logs \
    && chown app:app -R /opt/  \
    && pip install --upgrade pip  \
    && pip install -r ./requirements.txt --no-cache-dir

COPY . .

RUN chmod +x ./entrypoint.sh

EXPOSE 8000

USER app

ENTRYPOINT ["./entrypoint.sh"]