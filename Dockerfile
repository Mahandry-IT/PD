FROM docker:27-dind

RUN apk add --no-cache python3 build-base

WORKDIR /app
COPY . .

COPY docker-entrypoint.sh /usr/local/bin/docker-entrypoint.sh
RUN chmod +x /usr/local/bin/docker-entrypoint.sh

ENTRYPOINT ["docker-entrypoint.sh"]
CMD ["python3", "rendu/ilian.py"]
