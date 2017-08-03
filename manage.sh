#!/usr/bin/env bash

ACTION=${1:-run}

if [[ $ACTION == 'run' ]]; then
	docker run -d --rm -v $(pwd):/opt/hackcoinbot --env-file access.env hackcoinbot
elif [[ $ACTION == 'build' ]]; then
	docker build -t hackcoinbot .
else
	echo 'Invalid action'
	exit 1
fi
