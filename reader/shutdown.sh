#!/bin/bash
PROCESS=`lsof -t -i:9999`
kill -9 $PROCESS
echo kill $PROCESS, restart