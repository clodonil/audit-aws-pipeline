from flask import Flask
from flask_restful import reqparse, abort, Api, Resource
from app.dynamopipeline  import status


class Healthcheck(Resource):
    def get(self):
        '''
          
        '''

        (retorno, msg) = status()
        if retorno:
           msg =  {"status": 'success', 'message' : msg}
           return msg, 201
        else:
           msg =  {"status": 'error', 'message': msg}
           return msg, 401
