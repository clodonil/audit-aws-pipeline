from flask import Flask,Blueprint
from src.dynamopipeline  import status


# Rota /healthcheck
healthcheck = Blueprint('healthcheck',__name__)

@healthcheck.route('')
@healthcheck.route('/')
def Healthcheck():
    '''
          
    '''
    msg = "<h1> Sistema Online </h1>" 
   
    return msg, 200
