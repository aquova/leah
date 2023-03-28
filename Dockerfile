FROM python:3.11-alpine

RUN apk update && apk add \
    build-base

ADD requirements.txt /leah/requirements.txt
RUN pip3 install -r /leah/requirements.txt

WORKDIR /leah
CMD ["python3", "-u", "main.py"]
