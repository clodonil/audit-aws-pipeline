#!/bin/sh

sed -i 's/localhost/http\:\/\/localhot\:8080/g' teste.txt


echo "- targets: ['$API_URL']" >> /etc/prometheus/prometheus.yml


cat /etc/prometheus/prometheus.yml

/bin/prometheus --config.file=/etc/prometheus/prometheus.yml \
  --log.level=debug \
  --web.console.libraries=/etc/prometheus/console_libraries \
  --storage.tsdb.path=/prometheus                           \
  --web.console.templates=/etc/prometheus/consoles
