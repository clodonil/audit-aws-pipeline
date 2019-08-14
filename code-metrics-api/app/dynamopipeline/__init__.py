'''
documentacao
'''

import boto3

def dynamodb_query(table,region):
    dydb = boto3.resource('dynamodb',region_name=region)
    table = dydb.Table(table)
    dyretorno  = table.scan()

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

    
    for dy in dymetrics:
       for pipeline in dy['detail']:
           arn = [x for x in pipeline.keys()][0]
   
           if (pipeline[arn]['pipeline_status']) != 'Null':
              provider = arn.split(':')[2]
              projeto  = arn.split(':')[4]
              app      = arn.split(':')[5]
   
              pipe_status.append({'provider':provider,'projeto':projeto,'app':app,'status':pipeline[arn]['pipeline_status']})
              pipe_sum.append({'provider': provider,'max': len(dymetrics)})
              pipe_sum_success.append({'provider':provider,'projeto':projeto,'app':app,'max':pipeline[arn]['sum_success']})
              pipe_sum_fail.append({'provider':provider,'projeto':projeto,'app':app,'max':pipeline[arn]['sum_faild']})
              pipe_time_deploy.append({'provider':provider,'projeto':projeto,'app':app,'deploytime':pipeline[arn]['time_deploy']} )
   
   
              for stages in pipeline[arn]['stages']:
                 pipe_time_stages.append({'provider':provider,'projeto':projeto,'app':app,'stage':stages,'time':pipeline[arn]['stages'][stages]['time'] })
                 for actions in pipeline[arn]['stages'][stages]['actions']:
                     for action in actions:
                         pipe_time_actions.append({'provider':provider,'projeto':projeto,'app':app,'stage':stages, 'action': action,  'time': actions[action]['time']})
   
              for stage in pipeline[arn]['stage_faild']:
                  pipe_stage_fail.append({'provider':provider,'projeto':projeto,'app':app,'stage':stage, 'fail': pipeline[arn]['stage_faild'][stage]})
   
              for action in pipeline[arn]['action_faild']:              
                  pipe_action_fail.append({'provider':provider,'projeto':projeto,'app':app,'action':action, 'fail': pipeline[arn]['action_faild'][action]})
   
              for days in pipeline[arn]['deploy_day']:
                 for day in days:
                     pipe_deploy_day.append({'provider':provider,'projeto':projeto,'app':app,'day':day, 'qtd': days[day]})
   
       metrics['pipeline_status']  = pipe_status
       metrics['sum_pipeline']     = pipe_sum
       metrics['sum_success']      = pipe_sum_success
       metrics['sum_fail']         = pipe_sum_fail
       metrics['time_deploy']      = pipe_time_deploy
       metrics['time_stages']      = pipe_time_stages
       metrics['time_actions']     = pipe_time_actions
       metrics['stages_fail']      = pipe_stage_fail
       metrics['actions_fail']     = pipe_action_fail
       metrics['deploy_day']       = pipe_deploy_day
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
