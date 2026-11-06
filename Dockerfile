FROM ubuntu:22.04
ENV DEBIAN_FRONTEND=noninteractive PATH="/usr/games:${PATH}"
RUN apt-get update && apt-get install -y --no-install-recommends fortune-mod fortunes-min cowsay netcat-openbsd \
    && rm -rf /var/lib/apt/lists/* && useradd -m -u 10001 app
WORKDIR /app
RUN chown app:app /app
COPY --chown=app:app wisecow.sh .
RUN chmod +x wisecow.sh
USER 10001
EXPOSE 4499
CMD ["./wisecow.sh"]
