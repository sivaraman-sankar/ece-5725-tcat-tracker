#!/bin/bash

# Kill any process running on port 5000
lsof -ti :5000 | xargs kill -9 2>/dev/null[1]

# Launch Flask server in background with logging
nohup python -u $(pwd)/backend/app.py > output.log 2>&1 &
echo $! > flask.pid[5]

# Open port 5000 using UFW
sudo ufw allow 5000/tcp[3]