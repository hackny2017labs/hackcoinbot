FROM python:2.7

WORKDIR /opt

ENV is_docker=1

COPY . hackcoinbot/
RUN pip install -r hackcoinbot/requirements.txt

WORKDIR /opt/hackcoinbot

# run app
ENTRYPOINT ["/usr/local/bin/python", "/opt/hackcoinbot/app.py"]
