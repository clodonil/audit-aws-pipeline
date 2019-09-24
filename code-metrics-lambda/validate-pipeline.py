'''
Script para validar se os dados gravados no Dynamodb estão com a estrutura correta
'''

import datetime
import boto3
import json

def getpipelines():
    table = 'codemetrics-pipelines'
    client = boto3.resource('dynamodb',region_name='sa-east-1')
    table = client.Table(table)
    retorno = table.scan()
    return retorno['Items']


def falha_estrutura(pipelines):
    #validar informacao geral
    cont=0

    provider = pipelines['id'].split(':')[2]
    projeto  = pipelines['id'].split(':')[4]
    app      = pipelines['id'].split(':')[5]
    mask=("{0} - {1} - {2} -> ").format(provider, projeto, app)

    failure = False
    if pipelines['detail']['status']            == 'Null' : failure = True
    if pipelines['detail']['provider']          == 'Null' : failure = True
    if pipelines['detail']['finished_pipeline'] == 'Null' : failure = True
    if pipelines['detail']['start_pipeline']    == 'Null' : failure = True

    if not 'status'            in pipelines['detail'] : failure = True
    if not 'provider'          in pipelines['detail'] : failure = True
    if not 'finished_pipeline' in pipelines['detail'] : failure = True
    if not 'start_pipeline'    in pipelines['detail'] : failure = True

    for stages in pipelines['detail']['stages']:
      for stage in stages:

          if stages[stage]['finished'] == 'Null' : failure = True
          if stages[stage]['start']    == 'Null' : failure = True
          if stages[stage]['status']   == 'Null' : failure = True
          if stages[stage]['eventid']  == 'Null' : failure = True

          if not 'finished' in stages[stage] : failure = True
          if not 'start'    in stages[stage] : failure = True
          if not 'status'   in stages[stage] : failure = True
          if not 'eventid'  in stages[stage]  : failure = True


          for actions in stages[stage]['action']:
            for action in actions:
                if actions[action]['eventid']  == 'Null' : failure = True
                if actions[action]['provider'] == 'Null' : failure = True
                if actions[action]['finished'] == 'Null' : failure = True
                if actions[action]['start']    == 'Null' : failure = True
                if actions[action]['status']   == 'Null' : failure = True

                if not 'eventid'  in actions[action] : failure = True
                if not 'provider' in actions[action] : failure = True
                if not 'finished' in actions[action] : failure = True
                if not 'start' in actions[action]    : failure = True
                if not 'status' in actions[action]   : failure = True

    if failure:
      print(json.dumps(pipelines, indent=4, sort_keys=True))
    return failure


def change_in_segunds(hora):
    segunds = hora.total_seconds()
    return segunds

def metrics_faild(list_stages):
    fail         = []
    stages_fail  = {}
    actions_fail = {}
    for stages in list_stages:
        for stage in stages.keys():
            if stages[stage]['status'] == 'FAILED':
                if stage in stages_fail:
                    stages_fail[stage] +=1
                else:
                    stages_fail[stage] = 1
            lista_actions = [actions for actions in stages[stage]['action']]
            control_actions = {}
            for actions in lista_actions:
                for action in actions.keys():
                    if actions[action]['status'] == 'FAILED':
                        if action in actions_fail:
                            actions_fail[action] +=1
                        else:
                            actions_fail[action] = 1
    fail.append(stages_fail)
    fail.append(actions_fail)
    return fail

def metrics_time(list_stages, num_execucao):
    control_stages = {}
    for stages in list_stages:
        for stage in stages.keys():
            if stages[stage]['status'] == 'SUCCEEDED':
                time = datetime.datetime.strptime(stages[stage]['finished'],'%Y-%m-%dT%H:%M:%SZ') - datetime.datetime.strptime(stages[stage]['start'],'%Y-%m-%dT%H:%M:%SZ')
                control_stages[stage] =  {'time': str(change_in_segunds(time)/num_execucao),'actions':[]}
                lista_actions = [actions for actions in stages[stage]['action']]
                control_actions = {}
                for actions in lista_actions:
                    for action in actions.keys():
                        if actions[action]['status'] == 'SUCCEEDED':
                            action_time = datetime.datetime.strptime(actions[action]['finished'],'%Y-%m-%dT%H:%M:%SZ') - datetime.datetime.strptime(actions[action]['start'],'%Y-%m-%dT%H:%M:%SZ')
                            control_actions[action] = {'time': str(change_in_segunds(action_time)/num_execucao)}
                control_stages[stage]['actions'].append(control_actions)
    return control_stages

def salve_metrics(pipeline, metrics):
    arn = pipeline['id']
    pipeline_status = pipeline['detail']['status']
    metrics = metrics['detail']
    if not pipeline['running'] in metrics['running']:
        metrics['running'].append(pipeline['running'])
        sum_success = int(metrics['sum_success'])
        sum_faild   = int(metrics['sum_faild'])
        if pipeline_status == 'SUCCEEDED':
            sum_success += 1
            time_deploy  = datetime.datetime.strptime(pipeline['detail']['finished_pipeline'],'%Y-%m-%dT%H:%M:%SZ') - datetime.datetime.strptime(pipeline['detail']['start_pipeline'] ,'%Y-%m-%dT%H:%M:%SZ')
            metrics['time_deploy'] = str(change_in_segunds(time_deploy))
        elif pipeline_status == 'FAILED':
            sum_faild += 1
        metrics['sum_success']     = str(sum_success)
        metrics['sum_faild']       = str(sum_faild)
    stages  =  [stages for stages in pipeline['detail']['stages']]
    if pipeline_status == 'SUCCEEDED':
        metrics[arn]['pipeline_status'] = 1
        data = pipeline['detail']['finished_pipeline'].split('T')[0]
        deploy_day = [x for x in metrics['deploy_day'] if list(x.keys())[0] == data]
        if deploy_day:
            deploy_day[0][data] = str(int(deploy_day[0][data]) + 1)
        else:
            metrics['deploy_day'].append({data:'1'})
    elif pipeline_status == 'FAILED':
        metrics['pipeline_status'] = 0
        fail    = metrics_faild(stages)
        fail_stages  = fail[0]
        fail_actions = fail[1]
        for f_stages in fail_stages:
            if f_stages in metrics['stage_faild']:
                metrics['stage_faild'][f_stages] = str(int(metrics['stage_faild'][f_stages]) + int(fail_stages[f_stages]))
            else:
                metrics['stage_faild'][f_stages] = str(fail_stages[f_stages])
        for f_actions in fail_actions:
            if f_actions in metrics['action_faild']:
                metrics['action_faild'][f_actions] = str(int(metrics['action_faild'][f_actions]) + int(fail_actions[f_actions]))
            else:
                metrics['action_faild'][f_actions] = str(fail_actions[f_actions])
    metrics_stage = metrics_time(stages, len(metrics['running']) )
    metrics['stages'] = metrics_stage
    return metrics


def metricas(pipeline,metrics):
    resource_id = pipeline['id']
    if not resource_id in metrics:
         met = {}
         resource =  { 'pipeline_status' : 'Null',
                  'stages' : 'Null',
                  'running' : [],
                  'sum_success' : '0',
                  'sum_faild' : '0',
                  'stage_faild' : {},
                  'action_faild' : {},
                  'deploy_day' : [],
                  'runtime' : 'Null',
                  'time_deploy' : '0'
                  }
         met['resource_id'] = resource_id
         met['account']   = resource_id.split(':')[4]
         met['detail']    = resource
         metrics[resource_id] = salve_metrics(pipeline,met)
    else:
        pass

pipelines = getpipelines()
metrics = {}
for pipeline in pipelines:
    if not falha_estrutura(pipeline):
       metricas(pipeline, metrics)


print(json.dumps(metrics, indent=4, sort_keys=True))