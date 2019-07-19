FROM prom/prometheus:latest
LABEL maintainer Clodonil Trigo "clodonil@nisled.org"
USER 0
ENV API_URL='localhost:8080'

WORKDIR  /prometheus

COPY  prometheus.yml /etc/prometheus/
COPY  start.sh .

RUN chmod +x start.sh

ENTRYPOINT [ "./start.sh" ]
