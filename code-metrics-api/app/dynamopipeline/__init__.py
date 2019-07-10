'''
documentacao
'''

import datetime 
import boto3 
from app import app



def dyconn():
   try: 
      if app.config['ENDPOINT_URL']:
         client = boto3.resource(
                               'dynamodb',
                                region_name          = app.config['REGION_NAME'],
                                endpoint_url         = app.config['ENDPOINT_URL'],
                                aws_access_key_id    = app.config['ACCESS_ID'],
                                aws_secret_access_key= app.config['ACCESS_KEY']
                              )
    
      else:
         client = boto3.resource(
                               'dynamodb',
                                region_name          = app.config['REGION_NAME'],
                                aws_access_key_id    = app.config['ACCESS_ID'],
                                aws_secret_access_key= app.config['ACCESS_KEY']
                              )

      table = client.Table(app.config['TABLE_NAME']) 
      return table
   except:
      print("Erro ao comunicar com o DynamoDB")

 
def DySearch(id): 
    ''' 
    Consulta a tabela do dynamodb 
    '''

    dytable = dyconn()     
    msg   = dytable.get_item(Key= { 'id' : id }) 
    try:
        return msg['Item'] 
    except:
        raise ErroObtendoDados(msg="Erro ao obter o dados do id: {0}".format(id))

def get_projetos_pipelines(): 
    '''
     recupera informação da pipeline
    '''
    lista_pipeline = {}
    msg = DySearch('pipelines') 
    if 'detail' in msg: 
        for pipeline in msg['detail']:
            lista_pipeline[pipeline] = msg['detail'][pipeline]
        return lista_pipeline

def get_pipelines():
    '''
      retorna a lista de pipelines de todos os projetos.
    '''
  
    pipelines = []
    projetos = get_projetos_pipelines()
    for proj in projetos:
        for pipeline in projetos[proj]:
            raw_pipeline = DySearch(pipeline)
            pipelines.append(raw_pipeline)

    return pipelines
         
def pipelinefull(): 
    ''' 
     retorna informacao geral da pipeline
    ''' 
    status = False 
    query  = get_pipelines() 
     
    msg = [] 
    for pipeline in query: 
        try:
            status =  pipeline['detail']['pipeline_status']
            pi = { 'id': pipeline['id'], 
                'status': status, 
                'NumExecSuccess': NumExec('SUCCEEDED',pipeline) , 
                'NumExecFail'   : NumExec('FAILED',pipeline), 
                'AvgTime': AvgTime(pipeline) 
            } 
        except:
            pi = { 'id': pipeline['id'], 
                'status': 'running' 
            } 

        msg.append(pi) 
         
    if msg: 
       status   = True 
    else: 
       status   = False 
     
    return  (status, msg) 
     
def pipeline_detail(id):
    '''
      Retorna a informação detalhada de uma pipeline
    '''
    status = False 
    
    query = DySearch(id)

    return (201,query)
def NumExec(status, pipeline): 
    ''' 
       
    ''' 
    try: 
        cont = 0 
        for running in pipeline['detail']['running']: 
           for run in running:
              if 'finished' in running[run]:
                 if running[run]['status'] == status: 
                    cont += 1 
             
        return cont         
    except: 
        pass 
     
def AvgTime(pipeline): 
    ''' 
    media de todas as execucao das pipeline de um projeto
    ''' 
    total = 0 
    cont  = 0 
    avg   = "" 
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
     
    return str(avg) 
 
 
 
def AvgTimeStage(pipeline): 
    ''' 
    media dos tempos dos stages finalizados com sucesso
    ''' 
    control_stages = {} 
 
    for running in pipeline['detail']['running']: 
        for run in running:                
            for stages in running[run]['stages']: 
                for stage in stages: 
                    if stages[stage]['status'] == 'SUCCEEDED': 
                       time = datetime.datetime.strptime(stages[stage]['finished'],'%Y-%m-%dT%H:%M:%SZ') - datetime.datetime.strptime(stages[stage]['start'],'%Y-%m-%dT%H:%M:%SZ')    
                       if stage in control_stages: 
                          control_stages[stage] +=time 
                       else: 
                          control_stages[stage] =  time 
 
    
 
    for control in control_stages:         
        control_stages[control] /= len(pipeline['detail']['running'])                                   
     
    return control_stages 
        
def AvgTimeAction(pipeline):
    ''' 
    media dos tempos dos stages finalizados com sucesso
    '''
    control_stages = []

    for running in pipeline['detail']['running']:
        for run in running:
            for stages in running[run]['stages']:
                for stage in stages:
                    control_actions = {}
                    for actions in stages[stage]['action']:
                        for action in actions:
                            if actions[action]['status'] == 'SUCCEEDED':
                               time = datetime.datetime.strptime(actions[action]['finished'],'%Y-%m-%dT%H:%M:%SZ') - datetime.datetime.strptime(actions[action]['start'],'%Y-%m-%dT%H:%M:%SZ')
                               #if stage in control_actions:
                               if stage in control_actions:
                                     if action in control_actions[stage]:
                                        control_actions[stage][action] +=time
                                     else:
                                        control_actions[stage][action] = time
                               else:
                                     control_actions = {stage : {action : time}}
                    control_stages.append(control_actions)


    for list in control_stages: 
        for stage in list:
            for action in list[stage]:
                list[stage][action] /= len(pipeline['detail']['running'])
    return control_stages

def pipelineMetrics(): 
    ''' 
      defini as metricas que serão expostas 
    ''' 
    pipelines = get_pipelines()

    metrics = {} 
     
    metrics['realtime']         = realtime(pipelines) 
    metrics['sum_pipeline']     = sum_pipeline(pipelines) 
    metrics['sum_success']      = sum_success(pipelines) 
    metrics['sum_fail']         = sum_fail(pipelines) 
    metrics['deploy_day']       = deploy_day(pipelines) 
    metrics['time_deploy']      = time_deploy(pipelines) 
    metrics['time_stages']      = time_stages(pipelines)
    metrics['time_actions']      = time_action(pipelines)
    metrics['pipeline_status']  = pipeline_status(pipelines)
    
     
    return metrics 


def pipeline_status(pipelines):
    pipe_status=[] 
     
    for pipeline in pipelines: 
        try:
            provider = pipeline['id'].split(':')[2] 
            projeto  = pipeline['id'].split(':')[4] 
            app      = pipeline['id'].split(':')[5] 
            
            status   = pipeline['detail']['pipeline_status']

            if status == 'SUCCEEDED':
                succ = 0
            else: 
                succ = 1    

            info={'provider':provider,'projeto':projeto,'app':app,'status':succ} 
            pipe_status.append(info) 
        except:
            pass
    return pipe_status        


def realtime(pipelines):
    execute=[]
    
    for pipeline in pipelines:
        provider = pipeline['id'].split(':')[2] 
        projeto  = pipeline['id'].split(':')[4] 
        app      = pipeline['id'].split(':')[5] 
        num = 0

        for running in pipeline['detail']['running']:
            for run in running: 
                cont=0
                for stages in running[run]['stages']:
                    for stage in stages: 
                        if stages[stage]['finished'] == "Null":
                           cont = 1
                num += cont           

        run = {'provider':provider,'projeto':projeto,'app':app,'num':num} 
        execute.append(run)

    return(execute)

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
        try:
            provider = pipeline['id'].split(':')[2] 
            projeto  = pipeline['id'].split(':')[4] 
            app      = pipeline['id'].split(':')[5] 
            
            
            max =  NumExec('SUCCEEDED',pipeline)  
            
            projeto = {'provider':provider,'projeto':projeto,'app':app,'max':max} 
            success.append(projeto)
        except:
            pass    
     
    return(success) 
 
def sum_fail(pipelines): 
 
    fail = [] 
    for pipeline in pipelines:
        try: 
            provider = pipeline['id'].split(':')[2] 
            projeto  = pipeline['id'].split(':')[4] 
            app      = pipeline['id'].split(':')[5] 
            
            max =  NumExec('FAILED',pipeline)              
            projeto = {'provider':provider,'projeto':projeto,'app':app,'max':max} 
            fail.append(projeto)
        except:
            pass    

     
    return(fail) 
 
 
 
def deploy_day(pipelines): 
    today = [] 
     
    now = datetime.datetime.now().date()
     
    for pipeline in pipelines: 
        try:
            provider = pipeline['id'].split(':')[2] 
            projeto  = pipeline['id'].split(':')[4] 
            app      = pipeline['id'].split(':')[5] 
            max = 0 
            for running in pipeline['detail']['running']: 
                for run in running: 
                    start = datetime.datetime.strptime(running[run]['start'],'%Y-%m-%dT%H:%M:%SZ').date() 
                    if start == now: 
                       max += 1 
            
                    
            projeto = {'provider':provider,'projeto':projeto,'app':app,'max':max} 
            today.append(projeto) 
        except:
            pass    
    return(today) 
 
def change_in_segunds(hora): 
     
    hora,min,seg = str(hora).split(":") 
    segunds = (int(min)*60) + (int(hora)*120) + int(float(seg)) 
    return segunds 
     
def time_deploy(pipelines): 
    info_deploy = [] 
 
    for pipeline in pipelines: 
        try:
            provider = pipeline['id'].split(':')[2] 
            projeto  = pipeline['id'].split(':')[4] 
            app      = pipeline['id'].split(':')[5] 
            
            avgTimeDeploy =  AvgTime(pipeline) 
            
            if avgTimeDeploy: 
               info={'provider':provider,'projeto':projeto,'app':app,'time':change_in_segunds(avgTimeDeploy)} 
               info_deploy.append(info) 
        except:
            print(pipeline)    
     
    return(info_deploy) 
     
def time_stages(pipelines): 
    info_stages=[] 
     
    for pipeline in pipelines: 
        try:
            provider = pipeline['id'].split(':')[2] 
            projeto  = pipeline['id'].split(':')[4] 
            app      = pipeline['id'].split(':')[5] 
            
            avgTimeStage =  AvgTimeStage(pipeline) 
            
            if avgTimeStage: 
                for stage in avgTimeStage: 
                    info={'provider':provider,'projeto':projeto,'app':app,'stage':stage,'time':change_in_segunds(avgTimeStage[stage])} 
                    info_stages.append(info) 
        except:
            pass
 
    return(info_stages) 
 
def time_action(pipelines):
    info_action=[]

    for pipeline in pipelines:
        provider = pipeline['id'].split(':')[2]
        projeto  = pipeline['id'].split(':')[4]
        app      = pipeline['id'].split(':')[5]

        avgtimeaction =  AvgTimeAction(pipeline)
        for stages in avgtimeaction:
            for stage in stages:
                for action in stages[stage]:
                    info={'provider':provider,'projeto':projeto,'app':app,'stage':stage, 'action': action,  'time':change_in_segunds(stages[stage][action])}
                    info_action.append(info)

    return(info_action)

def status(): 
      msg = "Sistema Online" 
      retorno = True 
      return (retorno, msg) 