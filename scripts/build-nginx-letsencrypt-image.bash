version=$(< nginx-letsencrypt/VERSION) &&
docker build "$@" -t nginx-letsencrypt:"$version" nginx-letsencrypt &&
docker tag nginx-letsencrypt:"$version" nginx-letsencrypt:latest
