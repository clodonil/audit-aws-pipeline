from flask import Flask
from flask_restful import reqparse, abort, Api, Resource
from prometheus_flask_exporter import PrometheusMetrics
from prometheus_client import multiprocess
from prometheus_client import generate_latest, REGISTRY, Gauge, Counte


app = Flask(__name__)
metrics = PrometheusMetrics(app)
app.config.from_object('config')

# Router de versao para API
api = Api(app, prefix='/api/v1')


# Controllers
from app.controllers.pipelines  import *
from app.controllers.metrics    import *
from app.controllers.status     import * 


# Definiando os routers
api.add_resource(Pipeline,'/pipeline')
api.add_resource(Pipelines,'/pipelines')
api.add_resource(Metrics,'/metrics')
api.add_resource(Healthcheck,'/healthcheck')
