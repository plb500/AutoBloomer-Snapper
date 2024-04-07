#!/bin/bash

LOCAL_IP=`ifconfig | sed -En 's/127.0.0.1//;s/.*inet (addr:)?(([0-9]*\.){3}[0-9]*).*/\2/p'`

echo "Streaming camera"
echo "Stream can be viewed at:"
echo "   tcp/h264://${LOCAL_IP}:8888"

libcamera-vid -t0 --width 1920 --height 1080 --framerate 10 --nopreview --codec h264 --profile high --intra 5 --listen -o tcp://0.0.0.0:8888

