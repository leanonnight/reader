#!/bin/bash
PROCESS=`lsof -t -i:9999`
kill -9 $PROCESS
echo kill $PROCESS, restart
nohup python3.7 -u /home/reader/startup.py > /home/reader/log.txt 2>&1 &
