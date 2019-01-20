log() {
  printf 'fake-server.bash: %s\n' "$1"
}

log 'Pretending to be a server...'
log 'Sleeping for 10 seconds...'
sleep 10
log 'Oops I crashed!'
exit 1
