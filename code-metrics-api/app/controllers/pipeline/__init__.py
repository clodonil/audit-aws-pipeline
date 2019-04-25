from flask import Flask
from flask_restful import reqparse, abort, Api, Resource
from app.dynamopipeline  import getpipeline

parser = reqparse.RequestParser()
parser.add_argument('id'  ,type=str, location="json", required=True)


class Pipeline(Resource):
    def get(self):
        '''
           Retorna info da pipeline          
        '''
        args = parser.parse_args()
        id   = args['id']

        (retorno, msg) = getpipeline(id)
        if retorno:
           msg =  {"status": 'success', 'message' : msg}
           return msg, 201
        else:
           msg =  {"status": 'error', 'message': msg}
           return msg, 401
