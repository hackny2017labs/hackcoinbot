FROM python:2.7

# todo: add requirements.txt
RUN pip install slackclient

# todo: fill in env vars
ENV SLACK_BOT_ID <slack_bot_id>
ENV SLACK_BOT_TOKEN <slack_bot_token>

# clone repository
RUN git clone https://github.com/hackny2017labs/hackcoinbot /opt/

# run app
ENTRYPOINT ["/usr/local/bin/python", "/opt/hackcoinbot/app.py"]
