# syntax=docker/dockerfile:1
FROM linuxserver/swag:2.9.0-ls278
ARG DEPLOYMENT_ENVIRONMENT=production
COPY ./nginx/${DEPLOYMENT_ENVIRONMENT}/${DEPLOYMENT_ENVIRONMENT}.conf /config/nginx/site-confs/default
COPY ./nginx/fail2ban/jail.local /config/fail2ban/jail.local
COPY ./nginx/fail2ban/jail.local /etc/fail2ban/jail.local
