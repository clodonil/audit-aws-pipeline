from flask import Flask
from app.dynamopipeline  import pipelinefull, getpipeline
from prometheus_flask_exporter import PrometheusMetrics
from prometheus_client import multiprocess
from prometheus_client import generate_latest, REGISTRY, Gauge, Counter

IN_PROGRESS = Gauge("inprogress_requests", "help")
REQUESTS    = Counter('http_requests_total', 'Description of counter', ['method', 'endpoint'])

COLLECTION_TIME = Summary('jenkins_collector_collect_seconds', 'Time spent to collect metrics from Jenkins')

@app.route('/Metrics'):
def metrics():
    @dados = pipelineMetrics()


@IN_PROGRESS.track_inprogress()
@app.route('/homersimpson')
def homer():
    REQUESTS.labels(method='GET', endpoint="homersimpson").inc()
    return render_template('homer.html')

@IN_PROGRESS.track_inprogress()
@app.route('/covilha')
def covilha():
    REQUESTS.labels(method='GET', endpoint="covilha").inc()
    return render_template('covilha.html')
