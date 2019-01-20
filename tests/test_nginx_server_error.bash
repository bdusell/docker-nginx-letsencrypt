test_nginx_server_error() {
  timeout --foreground 20s sh -c '! docker run --rm -it test-nginx-server-error'
}

. scripts/build-nginx-letsencrypt-image.bash &&
docker build -t test-nginx-server-error tests/nginx-server-error
if test_nginx_server_error; then
  echo 'PASS'
else
  echo 'FAIL'
  exit 1
fi
