from flask import Flask, Blueprint
from app.dynamopipeline  import pipelinefull, getpipeline
from prometheus_flask_exporter import PrometheusMetrics
from prometheus_client import multiprocess
from prometheus_client import generate_latest, REGISTRY, Gauge, Counter, Summary

IN_PROGRESS = Gauge("inprogress_requests", "help")
REQUESTS    = Counter('http_requests_total', 'Description of counter', ['method', 'endpoint'])
COLLECTION_TIME = Summary('jenkins_collector_collect_seconds', 'Time spent to collect metrics from Jenkins')

metrics = Blueprint('metrics',__name__)

@IN_PROGRESS.track_inprogress()
@metrics.route('/', methods=["GET"])
def codemetrics():
    return "metricas"
    #@dados = pipelineMetrics()
