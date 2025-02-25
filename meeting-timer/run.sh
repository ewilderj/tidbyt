#!/bin/bash

source venv/bin/activate

# clear cache when we start, so restarting this script
# is a quick way of refreshing calendar contents
rm events.yml
while :; do
    python update.py
    sleep 30
done;
