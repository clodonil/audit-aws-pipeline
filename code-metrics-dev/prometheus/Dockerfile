FROM prom/prometheus
LABEL maintainer Clodonil Trigo "clodonil@nisled.org"
USER 0
ENV API_URL='localhost:8080'

WORKDIR    /prometheus

COPY prometheus/prometheus.yml /etc/prometheus/
COPY prometheus/start.sh .



ENTRYPOINT [ "./start.sh" ]
