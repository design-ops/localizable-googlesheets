FROM python:3.7

WORKDIR /work

ENV PYTHONPATH="$PYTHONPATH:./localisation"

COPY . /work

RUN pip install --no-cache-dir -r requirements.txt
