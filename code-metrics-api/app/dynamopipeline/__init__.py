import datetime
import boto3
from app import app

def DySearch(id='all'):
    '''
    Consulta a tabela do dynamodb
    '''
    
    client = boto3.resource('dynamodb',region_name=app.config['REGION_NAME'], endpoint_url=app.config['ENDPOINT_URL'])
    table = client.Table(app.config['TABLE_NAME'])


    
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

def AvgTimeStage(pipeline):
    '''
    '''
    total = 0
    cont  = 0
    avg   = ""
    stages =""
    for running in pipeline['detail']['running']:
        for run in running:
               if running[run]['status'] == 'SUCCEEDED':
                                     
                  cont += 1    
                  if total != 0:
                     total  += datetime.datetime.strptime(running[run]['finished'],'%Y-%m-%dT%H:%M:%SZ') - datetime.datetime.strptime(running[run]['start'],'%Y-%m-%dT%H:%M:%SZ')
                  else:
                     total  = datetime.datetime.strptime(running[run]['finished'],'%Y-%m-%dT%H:%M:%SZ') - datetime.datetime.strptime(running[run]['start'],'%Y-%m-%dT%H:%M:%SZ')

    if cont != 0:
       avg = total / cont
    
    return [stages,str(avg)]


    
        
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
    pipeline = DySearch()
    metrics = {}
    
    
    metrics['sum_pipeline']     = sum_pipeline(pipeline)
    metrics['sum_success']      = sum_success(pipeline)
    metrics['sum_fail']         = sum_fail(pipeline)
    metrics['deploy_day']       = deploy_day(pipeline)
    metrics['time_deploy']      = time_deploy(pipeline)
    metrics['time_stages']      = time_stages(pipeline)
    
    return metrics
    

def sum_pipeline(pipelines):
    sum = []
    providers = {}
    for pipeline in pipelines:
        provider = pipeline['id'].split(':')[2]
        if provider in providers:
           providers[provider] += 1
        else:
           providers[provider] = 1
    
    for provider in providers:    
        info = {'provider': provider,'max':providers[provider]}
    sum.append(info)
    return sum
    
def sum_success(pipelines):
    success = []
    for pipeline in pipelines:
        provider = pipeline['id'].split(':')[2]
        projeto  = pipeline['id'].split(':')[4]
        app      = pipeline['id'].split(':')[5]
        
        status =  pipeline['detail']['pipeline_status']
        max =  NumExec('SUCCEEDED',pipeline) 
        
        projeto = {'provider':provider,'projeto':projeto,'app':app,'max':max}
        success.append(projeto)    
    
    return(success)

def sum_fail(pipelines):

    fail = []
    for pipeline in pipelines:
        provider = pipeline['id'].split(':')[2]
        projeto  = pipeline['id'].split(':')[4]
        app      = pipeline['id'].split(':')[5]
        
        max =  NumExec('FAILED',pipeline) 
        
        projeto = {'provider':provider,'projeto':projeto,'app':app,'max':max}
        fail.append(projeto)    
    
    return(fail)



def deploy_day(pipelines):
    today = []
    
    now = datetime.datetime.now()
    
    for pipeline in pipelines:
        provider = pipeline['id'].split(':')[2]
        projeto  = pipeline['id'].split(':')[4]
        app      = pipeline['id'].split(':')[5]
        max = 0
        for running in pipeline['detail']['running']:
            for run in running:
                start = datetime.datetime.strptime(running[run]['start'],'%Y-%m-%dT%H:%M:%SZ').date()
                if start == now:
                   max += 1
        
        if max:           
           projeto = {'provider':provider,'projeto':projeto,'app':app,'max':max}
           today.append(projeto)
    return(today)

def change_in_segund(hora):
    
    hora,min,seg = hora.split(":")
    print(hora, min, seg)
    segund = (int(min)*60) + (int(hora)*120) + float(seg)
    return segund
    
def time_deploy(pipelines):
    info_deploy = []

    for pipeline in pipelines:
        provider = pipeline['id'].split(':')[2]
        projeto  = pipeline['id'].split(':')[4]
        app      = pipeline['id'].split(':')[5]
        
        avgTimeDeploy =  AvgTime(pipeline)
        
        #if avgTimeDeploy:
        #     segund = change_in_segund(avgTimeDeploy)
    info={'provider':provider,'projeto':projeto,'app':app,'time':segund}
    info_deploy.append(info)
    return(info_deploy)
    
def time_stages(pipelines):
    info_stages=[]
    
    for pipeline in pipelines:
        provider = pipeline['id'].split(':')[2]
        projeto  = pipeline['id'].split(':')[4]
        app      = pipeline['id'].split(':')[5]
        
        stage,avgTimeStage =  AvgTimeStage(pipeline)
        
        if avgTimeStage:
             segund = change_in_segund(avgTimeDeploy)
             info={'provider':provider,'projeto':projeto,'app':app,'time':segund}
             info_stages.append(info)

    return(info_stages)

def status():
      msg = "Sistema Online"
      retorno = True
      return (retorno, msg)
