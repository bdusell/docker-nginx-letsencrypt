docker-nginx-letsencrypt
========================

A truly containerized Nginx server with Let's Encrypt support. Comes with a
Certbot client that automatically renews certificates on a regular schedule.
Can be used as a reverse proxy to add https support to multiple sites on a
single server or cluster.

TL;DR
-----

* Most tutorials I've read for setting up Certbot on Docker do so in a way that
  is not fully self-contained and modular
  * e.g. Certbot renewals are usually managed by a cron job that is defined on
    the *host*, not inside a container
  * Docker cannot collect logs for services that run on the host; what if your
    renewals fail?
* This repo provides Docker images with a Certbot + Nginx combo that works out
  of the box and *is* fully self-contained within Docker
* Everything is logged to stdout, including Certbot renewal logs
* Instructions for setting up a domain with https support provided

Installation
------------

```sh
docker pull bdusell/nginx-letsencrypt
```

Introduction
------------

As you may know, [Let's Encrypt](https://letsencrypt.org/) and
[Certbot](https://certbot.eff.org/) are tools for enabling https on web
servers for free. As you also probably know,
[Docker](https://www.docker.com/) is an important technology these days that
allows web servers, and the software they depend on, to be self-contained and
modular. Ideally, we'd like to extend this principle to using Certbot with a
web server. However, most tutorials I've seen for setting up a web server in
Docker with Certbot do so in a way that is not fully self-contained. For
example, they often run automatic Certbot renewals by running `docker exec`
from a Cron job that is scheduled on the host. Without this external
configuration, Certbot *will not work properly*. Ideally, such a vital part of
the service should be configured automatically inside the container. Plus, we
want Docker to be able to capture the logs from Certbot as part of the web
server's logs, which is not done when using `docker exec`.

The main problem is that Certbot isn't really designed to run in a separate
container from the web server. On the other hand, Docker discourages running
multiple services inside of the same container. So, this repo defines a Docker
image that uses [Supervisor](http://supervisord.org/) to run an Nginx server
and cron in parallel, where cron is used to run `certbot renew` at regular
intervals. Although this violates the principle that every Docker container
should run one service, I think this is a reasonable exception given the
constraints. Even so, Supervisor is configured so that the two services
*behave* like one service. Logs from all services are logged to stdout so
that Docker can capture them, and the entire container exits immediately with
status 1 if any service fails.

Setup
-----

The base `nginx-certbot` image is meant to be extended by editing the
configuration file for Nginx at `/etc/nginx/nginx.conf`. Note that the Nginx
user should be set to `www-data`, not `nginx`. It is recommended to build a
new image that extends `nginx-certbot` and changes how Nginx is configured.
When running your server container, bind to ports 80 and 443 on the host. Note
that the container uses two volumes where it stores its certificates: one for
`/etc/letsencrypt`, and one for `/var/lib/letsencrypt`.

See [example-server/](example-server/) for a good starting point.

Adding Domains
--------------

This image works well for running multiple domains with https on a single
server or cluster running Docker. Here are steps for adding a new domain,
assuming you are adding a domain called `example.com` for the first time.

1. Add a new server block for `example.com` to `nginx.conf`. Make sure that it
   only listens to port 80 and not port 443. Certbot will automatically add a
   rule for port 443, and it will fail if one already exists. You might want
   to serve a dummy HTML page (such as the default `index.html` page) so you
   can easily verify that the server is working. See
   [example-server/nginx.conf](example-server/nginx.conf)
   for an example.
2. Double-check your new configuration for mistakes, then deploy your image
   with the updated configuration to the server hosting `example.com`. You may
   want to verify that the site is serving the dummy page over http.
3. Setting up Certbot for a domain requires one manual step initially. Inside
   your running server container, run `certbot --nginx` and work through the
   interactive prompts, e.g.
   ```
   $ docker exec -it your-server-container certbot --nginx
   ```
   Certbot will get a certificate for `example.com` from Let's Encrypt and
   make changes to `nginx.conf`. Certbot will give you the option to redirect
   all http requests to https.
4. Assuming that the step above was successful, your site now has https
   enabled. You should commit the changes that Certbot made to `nginx.conf`
   to version control. Copy it out of the container like so:
   ```
   $ docker cp your-server-container:/etc/nginx/nginx.conf .
   ```
5. Finally, change the newly-configured server block for `example.com` as
   desired (to set up a reverse proxy, add new HTML files, etc.).

Notes
-----

* Uses the BusyBox implementation of cron, which makes it easy to log
  everything to stdout

Known Issues
------------

* Supervisord takes quite a bit of memory
* For simplicity, the image is based on Ubuntu, not Alpine

Existing Docker + Let's Encrypt Tutorials and Tools
---------------------------------------------------

* [letsencrypt-nginx-proxy-companion](https://github.com/JrCs/docker-letsencrypt-nginx-proxy-companion)
* [How To Secure a Containerized Node.js Application with Nginx, Let's Encrypt, and Docker Compose](https://www.digitalocean.com/community/tutorials/how-to-secure-a-containerized-node-js-application-with-nginx-let-s-encrypt-and-docker-compose) (Jan 4, 2019)
* [Nginx and Let’s Encrypt with Docker in Less Than 5 Minutes](https://medium.com/@pentacent/nginx-and-lets-encrypt-with-docker-in-less-than-5-minutes-b4b8a60d3a71) (Sep 28, 2018)
* [Tying Let's Encrypt and Docker Swarm together](https://dev.to/fdoxyz/tying-lets-encrypt-and-docker-swarm-together-4j16) (Aug 10, 2018)
* [How to Set Up Free SSL Certificates from Let's Encrypt using Docker and Nginx](https://www.humankode.com/ssl/how-to-set-up-free-ssl-certificates-from-lets-encrypt-using-docker-and-nginx) (Jan 7, 2018)
* [Running NGINX and CertBot Containers on the Same Host](https://gist.github.com/rkaramandi/b9d693dd9ad941d5d346701f08368bba) (May 29, 2017)
* [docker-nginx-letsencrypt-sample](https://github.com/gilyes/docker-nginx-letsencrypt-sample) (Oct 19, 2016)
