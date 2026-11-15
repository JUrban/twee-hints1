#!/bin/bash
# RAM guard for a training job (15 Nov): every 2 s, kill any process whose argv contains PATTERN once its RSS
# exceeds GB; log to memwatch.log.   bash abs/pywatch.sh PATTERN GB
P=$1; G=$2
while true; do
  ps -eo pid=,rss=,args= | while read -r pid rss args; do
    case "$args" in *"$P"*) if [ "$rss" -gt $((G*1048576)) ]; then kill -9 "$pid" &&
      echo "$(date '+%F %T') KILL pywatch>$G G pid=$pid rss=$((rss/1048576))G $args" | cut -c1-200 >> /project/hintwork/memwatch.log; fi;; esac
  done
  sleep 2
done
