#!/bin/sh

docker run -tid  -p 27017:27017 \
    -v db_data:/data/db \
    --name mongodb  mongo

docker run -ti --rm --link mongodb:mongo \
        -p 5000:5000 \
        --name jlog_server jlog-api
