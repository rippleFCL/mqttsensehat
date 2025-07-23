FROM python:3.13-slim-bookworm AS requirement-builder

WORKDIR /app

RUN pip install --no-cache-dir poetry poetry-plugin-export

COPY ./pyproject.toml /app
COPY ./poetry.lock /app

RUN poetry export --without-hashes -f requirements.txt --output requirements.txt

RUN apt update && \
    apt install -y curl git g++

RUN pip install --no-cache-dir -r requirements.txt && \
    apt-get clean autoclean && \
    apt-get autoremove --yes && \
    rm -rf /var/lib/{apt,dpkg,cache,log}

FROM python:3.13-slim-bookworm

ENV PYTHONUNBUFFERED=1
WORKDIR /app

COPY --from=requirement-builder /usr/local/lib/python3.13/site-packages /usr/local/lib/python3.13/site-packages

COPY mqttsense/ /app/mqttsense
COPY main.py /app


ENTRYPOINT [ "python3", "main.py" ]
