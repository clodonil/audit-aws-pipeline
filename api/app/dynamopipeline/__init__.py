from config import DYNAMO_TABLE
import boto3




def DySearch(id='all'):
    '''
    Consulta a tabela do dynamodb
    '''
    
    client = boto3.resource('dynamodb')
    table = client.Table(DYNAMO_TABLE)
    
    if id == 'all': 
       msg   = table.scan()
    return msg['Items'] 

def pipelinefull():
    '''
    Retorna todas as pipeline na seguinte estrutura:
    { 
           'id': 'xxxx', 
           'status': 'SUCCEEDED', 
           'NumExec': '10' }

    '''
    
    msg = DySearch()
    retorno   = True
    return  (retorno, msg)
def getpipeline(id):
    '''
      Retorna a informacao detalhada de um pipeline
      
      Com a seguinte estrutura:
    
      "id": "xxxxx",  
      "detail": {
      "running": [
            {
               "5071630b": {
                    "account": "xxxxxx",
                    "finished": "2019-04-17T21:22:10Z",
                    "log": { },
                    "source": "aws.codepipeline",
                    "start": "2019-04-17T21:19:54Z",
                    "status": "FAILED",
                    "stages": [
                          {
                            "Source": {
                                 "execute": [],
                                 "output": [],
                                 "provider": "CodeCommit",
                                 "start": "2019-04-17T21:20:00Z",
                                 "finished": "2019-04-17T21:22:07Z",
                                 "status": "SUCCEEDED"
                                }
                          }
                    ]
                 }
              }
           ]
        }
      }
    '''
    msg = DySearch(id)
    retorno = True
    return  (retorno, msg)


def status():
      msg = "Sistema Online"
      retorno = True
      return (retorno, msg)
