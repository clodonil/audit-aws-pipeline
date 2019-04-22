from flask import Flask
from flask_restful import reqparse, abort, Api, Resource
from app.dynamopipeline  import pipelinefull

class Pipelines(Resource):
    def get(self):
        '''
          
        '''

        (retorno, msg) = pipelinefull()
        if retorno:
           msg =  {"status": 'success', 'message' : msg}
           return msg, 201
        else:
           msg =  {"status": 'error', 'message': msg}
           return msg, 401