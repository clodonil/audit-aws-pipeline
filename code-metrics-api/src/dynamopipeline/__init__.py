import boto3

def dynamodb_query(table,region):
    dydb = boto3.resource('dynamodb',region_name=region)
    table = dydb.Table(table)
    dyretorno = {}
    try:
      dyretorno = table.scan()
    except:
      print("botocore.exceptions.NoCredentialsError: Unable to locate credentials")

    if "Items" in dyretorno:
        return dyretorno['Items']
    else:
        return []


def loadMetrics(dymetrics):

    metrics = {}
    pipe_status       = []
    pipe_sum          = []
    pipe_sum_success  = []
    pipe_sum_fail     = []
    pipe_time_deploy  = []
    pipe_time_stages  = []
    pipe_time_actions = []
    pipe_stage_fail   = []
    pipe_action_fail  = []
    pipe_deploy_day   = []
    pipe_runtime = []
    pipe_version = []

    
    for dy in dymetrics:
       arn = dy['resource_id']
       pipeline = dy['detail']
       
       if (pipeline['pipeline_status']) != 'Null':
          provider = arn.split(':')[2]
          projeto  = arn.split(':')[4]
          app      = arn.split(':')[5]     
          pipe_status.append({'provider':provider,'projeto':projeto,'app':app,'status':pipeline['pipeline_status']})
          pipe_sum.append({'provider': provider,'max': len(dymetrics)})
          pipe_sum_success.append({'provider':provider,'projeto':projeto,'app':app,'max':pipeline['sum_success']})
          pipe_sum_fail.append({'provider':provider,'projeto':projeto,'app':app,'max':pipeline['sum_faild']})
          pipe_time_deploy.append({'provider':provider,'projeto':projeto,'app':app,'deploytime':pipeline['time_deploy']})
          pipe_runtime.append({'provider':provider,'projeto':projeto,'app':app,'runtime':pipeline['runtime']})
          pipe_version.append({'provider':provider,'projeto':projeto,'app':app,'pipe_version':pipeline['pipe_version']})
          
          for stages in pipeline['stages']:
             pipe_time_stages.append({'provider':provider,'projeto':projeto,'app':app,'stage':stages,'time':pipeline['stages'][stages]['time'] })
          
             for actions in pipeline['stages'][stages]['actions']:
                 for action in actions:
                     pipe_time_actions.append({'provider':provider,'projeto':projeto,'app':app,'stage':stages, 'action': action,  'time': actions[action]['time']})
          
          for stage in pipeline['stage_faild']:
              pipe_stage_fail.append({'provider':provider,'projeto':projeto,'app':app,'stage':stage, 'fail': pipeline['stage_faild'][stage]})
          
          for action in pipeline['action_faild']:              
              pipe_action_fail.append({'provider':provider,'projeto':projeto,'app':app,'action':action, 'fail': pipeline['action_faild'][action]})
          
          for days in pipeline['deploy_day']:
             for day in days:
                 pipe_deploy_day.append({'provider':provider,'projeto':projeto,'app':app,'day':day, 'qtd': days[day]})
   
    metrics['pipeline_status'] = pipe_status
    metrics['sum_pipeline'] = pipe_sum
    metrics['sum_success'] = pipe_sum_success
    metrics['sum_fail'] = pipe_sum_fail
    metrics['time_deploy'] = pipe_time_deploy
    metrics['time_stages'] = pipe_time_stages
    metrics['time_actions'] = pipe_time_actions
    metrics['stages_fail'] = pipe_stage_fail
    metrics['actions_fail'] = pipe_action_fail
    metrics['deploy_day'] = pipe_deploy_day
    metrics['runtime'] = pipe_runtime
    metrics['pipe_version'] = pipe_version



    return metrics



def pipelineMetrics():
    dytbmetricas  = 'codemetrics-metricas'
    dyregion      = 'sa-east-1'
    dymetrics = dynamodb_query(dytbmetricas,dyregion)
    metrics = loadMetrics(dymetrics)
    return metrics

def status(): 
      msg = "Sistema Online" 
      retorno = True 
      return (retorno, msg) 
