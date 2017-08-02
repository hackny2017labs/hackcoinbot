FROM python:2.7

WORKDIR /opt

COPY . hackcoinbot/
RUN pip install -r hackcoinbot/requirements.txt

WORKDIR /opt/hackcoinbot

# run app
ENTRYPOINT ["/usr/local/bin/python", "/opt/hackcoinbot/app.py"]
