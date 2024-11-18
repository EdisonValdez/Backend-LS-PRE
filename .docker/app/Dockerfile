# syntax=docker/dockerfile:1
FROM python:3.10-slim
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ARG DEPLOYMENT_ENVIRONMENT=staging
WORKDIR /code
COPY . /code/
RUN pip3 install pipenv==2022.6.7
#    apt-get update && apt-get install git openssh-client gettext build-base libffi-dev musl-dev zlib-dev jpeg-dev \
RUN apt-get update && apt-get -y --no-install-recommends install software-properties-common \
  && apt-get update \
  && apt-get install -y gdal-bin pkg-config python3-dev gcc libc-dev libffi-dev\
  && apt-get install -y libcairo2-dev libjpeg-dev libgif-dev

RUN if [ "$DEPLOYMENT_ENVIRONMENT" = 'staging' ]; then pipenv lock -dr --keep-outdated >/requirements.txt; else pipenv lock -r --keep-outdated >/requirements.txt; fi

RUN pipenv --rm
RUN pip3 install -r /requirements.txt
