from flask import Flask
from flask_restful import reqparse, abort, Api, Resource
from src.dynamopipeline  import pipelinefull, pipeline_detail

parser = reqparse.RequestParser()
parser.add_argument('id'  ,type=str, location="json", required=True)


class Pipelines(Resource):
    def get(self):
        '''
          Retorna todas as pipelines
        '''

        (retorno, msg) = pipelinefull()
        if retorno:
           msg =  {"status": 'success', 'message' : msg}
           return msg, 201
        else:
           msg =  {"status": 'error', 'message': msg}
           return msg, 401
           



class Pipeline(Resource):
    def get(self):
        '''
           Retorna info da pipeline          
        '''
        args = parser.parse_args()
        id   = args['id']
        (retorno, msg) = pipeline_detail(id)
        if retorno:
           msg =  {"status": 'success', 'message' : msg}
           return msg, 201
        else:
           msg =  {"status": 'error', 'message': msg}
           return msg, 401
           
