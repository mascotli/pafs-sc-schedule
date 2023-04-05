# FROM alpine:3.14
FROM tiangolo/uvicorn-gunicorn-fastapi:python3.9

# ENV TIME_ZONE Asia/Shanghai
ENV PYTHONPATH "${PYTHONPATH}:/"
ENV PORT=8000

RUN pip install --upgrade pip

COPY ./bin/*.sh /app/
COPY ./requirements.txt /app/

RUN pip install -r requirements.txt

# RUN apt-get update \
#     && apt-get install -y net-tools \
#     && apt-get install -y iputils-ping

COPY ./app /app