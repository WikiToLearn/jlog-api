#!/bin/sh

docker run -tid --name mongodb mongo

docker run -ti --rm --link mongodb:mongo \
        -p 5000:5000 \
        --name jlog_server jlog-api
