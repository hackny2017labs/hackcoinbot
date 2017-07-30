#!/usr/bin/env bash

TRUE=1
FALSE=0

REFRESH=${1:-0}

# clean up container
trap "cleanUp" SIGINT SIGTERM EXIT

function cleanUp() {
	PID=$(docker ps -q --filter name=hackcoinbot-redis)
	docker kill $PID
}

if [[ $REFRESH -eq $TRUE ]]; then
	docker run \
		-v $(pwd)/.redis-data:/data \
		-p 6379:6379 \
		--name hackcoinbot-redis \
		-d redis:4
else
	docker start $(docker ps --filter status=exited --filter name=hackcoinbot-redis -q)
fi

python2 app.py
