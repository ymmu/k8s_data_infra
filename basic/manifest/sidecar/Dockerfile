## content cloner image
# FROM alpine:3.12
# RUN apk add --no-cache git
FROM ubuntu:16.04
RUN apt-get update && apt-get install -y git
COPY ./content_cloner /content_cloner
RUN chmod a+x /content_cloner
WORKDIR /
CMD ["/content_cloner"]
