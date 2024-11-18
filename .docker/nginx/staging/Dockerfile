# syntax=docker/dockerfile:1
FROM linuxserver/swag
ARG DEPLOYMENT_ENVIRONMENT=staging
COPY ./nginx/${DEPLOYMENT_ENVIRONMENT}/${DEPLOYMENT_ENVIRONMENT}.conf /config/nginx/site-confs/default
COPY ./nginx/fail2ban/jail.local /config/fail2ban/jail.local
COPY ./nginx/fail2ban/jail.local /etc/fail2ban/jail.local
