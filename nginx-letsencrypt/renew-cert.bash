log() {
  printf 'renew-cert.bash: %s\n' "$1"
}

n=$(($RANDOM % 3600)) && \
log "sleeping for $n seconds..." && \
sleep "$n" && \
log 'checking for renewal...' && \
certbot renew && \
log 'success'
