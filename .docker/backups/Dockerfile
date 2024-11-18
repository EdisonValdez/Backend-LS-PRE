# syntax=docker/dockerfile:1
FROM alpine:3.6

# copy crontabs for root user
RUN mkdir /backups/
COPY cron/dump.sh /etc/periodic/daily/dump
RUN chmod +x /etc/periodic/daily/dump

RUN mkdir /backups_cron/
COPY cron/dump.sh /backups_cron/dump.sh
RUN chmod +x /backups_cron/dump.sh
COPY cron/dropbox.sh /backups_cron/dropbox.sh
RUN chmod +x /backups_cron/dropbox.sh
# start crond with log level 8 in foreground, output to stderr
CMD ["crond", "-f", "-d", "8"]
# we need to install postgres in order to have pg_dump funcion
# TODO pending COPY PG_DUMP remove postgres: https://stackoverflow.com/questions/46548552/upgrade-to-postgres96-on-alpine-usr-bin-pg-dump-no-such-file-or-directory
RUN apk update
RUN apk --update --cache add postgresql
RUN apk --update --cache add postgresql-client
RUN apk --update --cache add curl
