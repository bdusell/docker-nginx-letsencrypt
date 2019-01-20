test_nginx_config_error() {
  timeout --foreground 10s sh -c '! docker run --rm -it test-nginx-config-error'
}

. scripts/build-nginx-letsencrypt-image.bash &&
docker build -t test-nginx-config-error tests/nginx-config-error
if test_nginx_config_error; then
  echo 'PASS'
else
  echo 'FAIL'
  exit 1
fi
