FROM ubuntu:18.04
WORKDIR /app/
# Install the following programs:
# - Certbot
# - supervisord
# - nginx
# - the BusyBox implementation of cron
# Install Certbot.
# See https://certbot.eff.org/lets-encrypt/ubuntubionic-nginx
RUN apt-get update && \
    apt-get install --no-install-recommends --no-install-suggests -y \
        software-properties-common && \
    add-apt-repository universe && \
    add-apt-repository ppa:certbot/certbot && \
    apt-get update && \
# Also install supervisord to run both nginx and cron simultaneously.
    apt-get install --no-install-recommends --no-install-suggests -y \
        certbot \
        python-certbot-nginx \
        supervisor=3.* \
        nginx=1.* \
        wget=1.* && \
# Download the busybox implementation of cron, since it's much easier to get it
# to log to stdout/stderr.
    wget https://busybox.net/downloads/binaries/1.30.0-i686/busybox_CROND && \
    chmod a+x busybox_CROND && \
# Configure nginx to write logs to stdout/stderr, as done in the official nginx
# image.
    ln -sf /dev/stdout /var/log/nginx/access.log && \
    ln -sf /dev/stderr /var/log/nginx/error.log && \
# Clean up apt packages and cache.
    apt-get remove --purge --auto-remove -y \
        wget && \
    rm -rf /var/lib/apt/lists/*
# Configure supervisord.
COPY supervisord.conf /etc/supervisord.conf
# Configure cron.
COPY root /var/spool/cron/crontabs/
COPY renew-cert.bash /app/renew-cert.bash
# Expose ports 80 (http) and 443 (https).
EXPOSE 80 443
# These volumes are exposed in the official certbot/certbot image too.
VOLUME /etc/letsencrypt /var/lib/letsencrypt
# Use an appropriate stop signal for supervisord.
STOPSIGNAL SIGTERM
# Using -c with supervisord suppresses a warning at startup.
# If supervisord stops for any reason, then exit with exit code 1. It should
# never stop running. This works around the fact that supervisord always exits
# with code 0, even if it was sent SIGTERM.
CMD ["sh", "-c", "supervisord -c /etc/supervisord.conf; exit 1"]
