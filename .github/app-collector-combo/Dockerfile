FROM golang:1.16

WORKDIR $GOPATH/main

ARG GOPROXY=direct

ENV GOPROXY=direct

RUN go get github.com/rakyll/hey

CMD hey -z 10s http://127.0.0.1:8080/outgoing-http-call
