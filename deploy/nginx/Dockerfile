FROM nginx:alpine

RUN apk add --no-cache certbot

COPY default.conf /etc/nginx/conf.d/default.conf

EXPOSE 80 443
