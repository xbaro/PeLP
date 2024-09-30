FROM ubuntu:latest

ARG DEBIAN_FRONTEND="noninteractive"
ENV TZ=Europe/Madrid

RUN apt-get update && apt-get install -y build-essential make gcc valgrind nano && apt-get clean
