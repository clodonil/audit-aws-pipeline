from config import DYNAMO_TABLE
import datetime
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
    else:
       msg   = table.get_item(Key= { 'id' : id })
       return msg['Item'] 
       
    

def NumExec(status, pipeline):
    '''
      
    '''
    try:
        cont = 0
        for running in pipeline['detail']['running']:
           for run in running:
              if running[run]['status'] == status:
                 cont += 1
            
        return cont        
    except:
        pass
def AvgTime(pipeline):
    '''
    '''
    total = 0
    cont  = 0
    avg   = ""
    for running in pipeline['detail']['running']:
        for run in running:
            try:
               if running[run]['status'] == 'SUCCEEDED':
                  cont += 1    
                  if total != 0:
                     total  += datetime.datetime.strptime(running[run]['finished'],'%Y-%m-%dT%H:%M:%SZ') - datetime.datetime.strptime(running[run]['start'],'%Y-%m-%dT%H:%M:%SZ')
                  else:
                     total  = datetime.datetime.strptime(running[run]['finished'],'%Y-%m-%dT%H:%M:%SZ') - datetime.datetime.strptime(running[run]['start'],'%Y-%m-%dT%H:%M:%SZ')
            except:
                pass
    
    if cont != 0:
       avg = total / cont
    
        
    
    return str(avg)
    
        
def pipelinefull():
    '''
    Retorna todas as pipeline na seguinte estrutura:
    { 
           'id': 'xxxx', 
           'status': 'SUCCEEDED', 
           'NumExecSuccess': '10' ,
           'NumExecFail' : '3',
           'AvgTime': '0:15:22'
        
    }

    '''
    status = False
    query = DySearch()
    
    msg = []
    for pipeline in query:
        pi = { 'id': pipeline['id'],
               'status': pipeline['detail']['pipeline_status'],
               'NumExecSuccess': NumExec('SUCCEEDED',pipeline) ,
               'NumExecFail'   : NumExec('FAILED',pipeline),
               'AvgTime': AvgTime(pipeline)
        }
        msg.append(pi)
        
    if msg:
       status   = True
    else:
       status   = False
    
    return  (status, msg)
    
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
                                 "finished": "2019-04-17T21:22:07Z",
                                 "status": "SUCCEEDED"
                                }
                          }
                                 "provider": "CodeCommit",
                                 "start": "2019-04-17T21:20:00Z",
                    ]
                 }
              }
           ]
        }
      }
    '''
    msg = DySearch(id)
    if msg:
       return  (True, msg)
    else:
       return (False, msg)    
       
def pipelineMetrics():
    '''
      defini as metricas que serão expostas
    '''
    query = DySearch()
    
       
    

def status():
      msg = "Sistema Online"
      retorno = True
      return (retorno, msg)

