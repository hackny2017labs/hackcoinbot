#!/usr/bin/env bash

TRUE=1
FALSE=0

REFRESH=${1:-0}

# clean up container
trap "cleanUp" SIGINT SIGTERM EXIT

function cleanUp() {
	REDIS=$(docker ps -q --filter name=hackcoinbot-redis)
	docker kill $REDIS > /dev/null 2>&1
}

CONTAINER_PID=$(docker ps --filter status=exited --filter name=hackcoinbot-redis -q)

if [[ ! -f 'user_data.json' ]]; then
	echo '{}' > user_data.json
fi

if [[ $REFRESH -eq $TRUE || -z $CONTAINER_PID ]]; then
	docker run \
		-v $(pwd)/.redis-data:/data \
		-p 6379:6379 \
		--name hackcoinbot-redis \
		-d redis:4
else
	docker start $CONTAINER_PID
fi

python2 app.py
