## Alpine Linux  https://hub.docker.com/_/alpine/
FROM alpine:latest

## Node.js  https://pkgs.alpinelinux.org/package/edge/main/x86_64/nodejs
RUN apk update && apk add --no-cache nodejs npm

## 의존 모듈
WORKDIR /
ADD ./package.json /
RUN npm install
ADD ./webapl.js /

## 애플리케이션 기동
CMD node /webapl.js
