from flask import Flask, Blueprint
from flask_restful import reqparse, abort, Api, Resource
from prometheus_flask_exporter import PrometheusMetrics

# instanciando o app flask
app = Flask(__name__)

# Load the default configuration
app.config.from_object('config')

metrics = PrometheusMetrics(app)

# Router de versao para API
api = Api(app, prefix='/api/v1')


# Controllers
#from app.controllers.pipelines    import * 
from app.controllers.metrics      import metrics
from app.controllers.healthcheck  import healthcheck


# Definiando os routers
#api.add_resource(Pipeline,   '/pipeline')
#api.add_resource(Pipelines,  '/pipelines')


app.register_blueprint(healthcheck,url_prefix='/healthcheck')
app.register_blueprint(metrics, url_prefix='/metrics')