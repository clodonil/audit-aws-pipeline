from flask import request, Blueprint, Response
from app.dynamopipeline import pipelineMetrics
from prometheus_client import Counter, Histogram, Gauge, CollectorRegistry,generate_latest
import prometheus_client

# Rota /metrics
metrics = Blueprint('metrics',__name__)

CONTENT_TYPE_LATEST = str('text/plain; version=0.0.4; charset=utf-8')

registry = CollectorRegistry()

SUM_PIPELINE = Counter('sum_pipeline', 'Total Pipelines',['provider'],registry=registry)
SUM_SUCCESS  = Counter('sum_pipeline_success', 'Deployment successfully',['provider','projeto','app'],registry=registry)
SUM_FAIL     = Counter('sum_pipeline_failure', 'Deployment Failure',['provider','projeto','app'],registry=registry)
DEPLOY_DAY   = Gauge('deploy_day', 'Deployment Frequency',['provider','projeto','app'],registry=registry)
TIME_DEPLOY  = Histogram('time_deploy_seconds', 'Deployment Speedy',['provider', 'projeto','app'],registry=registry)
TIME_STAGES  = Histogram('time_stage_seconds', 'Deployment Speedy',['provider', 'projeto','app','stage'],registry=registry  )


@metrics.route('')
def codemetrics():
    
    metrics = pipelineMetrics()
    
    # total de pipeline
    for sum_pipeline in metrics['sum_pipeline']:
        SUM_PIPELINE.labels(sum_pipeline['provider']).inc(sum_pipeline['max'])
    
    # Sum deploy of success
    for sum_success in metrics['sum_success']:
        SUM_SUCCESS.labels(sum_success['provider'],sum_success['projeto'],sum_success['app']).inc(sum_success['max'])
    
    # Sum deploy of fail
    for sum_fail in metrics['sum_fail']:
        SUM_FAIL.labels(sum_fail['provider'],sum_fail['projeto'],sum_fail['app']).inc(sum_fail['max'])
    
    # Sum deploy of today
    for deploy_day in metrics['deploy_day']:
        DEPLOY_DAY.labels(deploy_day['provider'],deploy_day['projeto'],deploy_day['app']).set(deploy_day['max'])
    
    for info_deploy in metrics['time_deploy']:
        TIME_DEPLOY.labels(info_deploy['provider'],info_deploy['projeto'],info_deploy['app']).observe(info_deploy['time'])
        
        
    for info_stages in metrics['time_stages']:
        print(info_stages)
        TIME_STAGES.labels(info_stages['provider'],info_stages['projeto'],info_stages['app'],info_stages['stage']).observe(info_stages['time'])


    return Response(prometheus_client.generate_latest(registry), mimetype=CONTENT_TYPE_LATEST)
