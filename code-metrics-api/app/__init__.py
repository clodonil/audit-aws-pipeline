from flask import Flask
from flask_restful import reqparse, abort, Api, Resource

app = Flask(__name__,)
app.config.from_object('config')

api = Api(app, prefix='/api/v1')


# Controllers
from app.controllers.pipelines  import *
#from app.controllers.metricas   import *
from app.controllers.status     import * 


# Definiando os routers
api.add_resource(Pipeline,'/pipeline')
api.add_resource(Pipelines,'/pipelines')
#api.add_resource(Metricas,'/metricas')
api.add_resource(Healthcheck,'/healthcheck')