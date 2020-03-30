#!/bin/bash
docker run -i -t -e INTERFACE=wlx7cdd9080f7f6 -e OUTGOINGS=wlp1s0 --net host --privileged sonoff-tasmotizer
