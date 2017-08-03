FROM python:2.7

# todo: add requirements.txt
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . /opt/hackcoinbot

WORKDIR /opt/hackcoinbot

# run app
ENTRYPOINT ["/usr/local/bin/python", "/opt/hackcoinbot/app.py"]
