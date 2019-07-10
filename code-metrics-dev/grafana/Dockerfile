FROM prom/prometheus
LABEL maintainer Clodonil Trigo "clodonil@nisled.org"
USER 0

ENV PROMETHEUS='localhost:9090'

WORKDIR    /prometheus

COPY provisioning /etc/grafana/provisioning/
COPY dashboards /ect
COPY prometheus/start.sh .


USER grafana
ENTRYPOINT [ "/run.sh" ]

ENTRYPOINT [ "./start.sh" ]
