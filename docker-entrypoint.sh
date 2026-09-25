#!/bin/sh
set -e

# demarre le daemon Docker interne au conteneur (dind), pour que les
# conteneurs lances par etape6_docker() partagent le meme reseau (donc
# 127.0.0.1) que le script Python qui les interroge.
dockerd --host=unix:///var/run/docker.sock >/var/log/dockerd.log 2>&1 &

until docker info >/dev/null 2>&1; do
    sleep 0.5
done

exec "$@"
