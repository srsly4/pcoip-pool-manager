#!/bin/bash

PID_FILE="/var/run/pcoip-pool-manager/pcoip-pool-manager-api.pid"
PORT=8000
COMMAND="python3 manage.py runserver 0.0.0.0:${PORT}"

die () {
    log_error $@
    exit 1
}

log () {
  echo "[`date +'%Y-%m-%d %T'`] $@";
}

log_error () {
  echo >&2 "[`date +'%Y-%m-%d %T'`] $@"
}

start_service() {
  log "Running command ${COMMAND}..."
  ${COMMAND} &
  ./docker/wait-for-it.sh localhost:${PORT} -t 60
  if [ $? -ne 0 ]; then
    log_error "Starting service was unsuccessful, will try again."
    start_service
  fi
}

if [ "$1" = "start-live" ]; then
  start_service

  while inotifywait -q -r --exclude '(\.git/|\.idea/|\backup/|\data/)' -e modify,create,delete,move,move_self /server; do
    log "Configuration changes detected. Will restart..."
    PID=$(<$PID_FILE)
    kill $PID
    while [ -e /proc/$PID ]; do
      sleep .6
    done
    start_service
  done
else
  exec "$@"
fi
