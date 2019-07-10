'''
Script para validar se os dados gravados no Dynamodb estão com a estrutura correta
'''

import datetime
import boto3
import json



def getpipelines():
    table = 'pipelines'
    client = boto3.resource('dynamodb',region_name='us-east-1')
    table = client.Table(table)
    query= { 'id' : 'pipelines' }
    retorno = table.get_item(Key=query)
    return retorno['Item']

def getpipeline(id):
    table = 'pipelines'
    client = boto3.resource('dynamodb',region_name='us-east-1')
    table = client.Table(table)
    query = { 'id' : id }
    retorno = table.get_item(Key=query)
    return retorno


def valida(pipelines):


    #validar informacao geral
    cont=0

    provider = pipelines['id'].split(':')[2]
    projeto  = pipelines['id'].split(':')[4]
    app      = pipelines['id'].split(':')[5]
    mask=("{0} - {1} - {2} -> ").format(provider, projeto, app)
    print(pipelines['id'])

    if pipelines['detail']['pipeline_status'] : print("Status Geral: OK")
    print("Status Geral: OK "  if 'pipeline_status' in pipelines['detail'] else 'Geral:' + mask)

    for running in pipelines['detail']['running']:

        for run in running:
            print("----> RUNNING:",run)
            print("------> Running Account: OK"  if 'account'  in running[run] else 'Running:' + mask + 'Account' )
            print("------> Running Finished: OK" if 'finished' in running[run] else 'Running:' + mask + 'Finished')
            print("------> Running Source: OK"   if 'source'   in running[run] else 'Running:' + mask + 'Source'  )
            print("------> Running Start: OK"    if 'start'    in running[run] else 'Running:' + mask + 'Start'   )
            print("------> Running Status: OK"   if 'status'   in running[run] else 'Running:' + mask + 'Status'  )

            for stages in running[run]['stages']:
                for stage in stages:
                    print("--------> STAGE",stage)
                    print("-----------> Stage finished: OK " if 'finished'  in stages[stage] else 'Stage:' + mask + 'Finished')
                    print("-----------> Stage start: OK "    if 'start'     in stages[stage] else 'Stage:' + mask + 'start'   )
                    print("-----------> Stage status: OK "   if 'status'    in stages[stage] else 'Stage:' + mask + 'status'  )

                    if stages[stage]['finished'] == "Null":
                        print(json.dumps(running, indent=4, sort_keys=True))

                    for actions in stages[stage]['action']:
                        for action in actions:
                            print("-------------> ACTION:", action)
                            print("----------------> Action EventId: OK "  if 'eventid'   in actions[action] else 'Action:' + mask + 'EventId' )
                            print("----------------> Action provider: OK " if 'provider'  in actions[action] else 'Action:' + mask + 'Provider')

                            if actions[action]['finished'] == "Null":
                               print(json.dumps(actions, indent=4, sort_keys=True))





ids = getpipelines()

for pipe_id in ids['detail']:
    for id in  ids['detail'][pipe_id]:
        pipelines = getpipeline(id)
        valida(pipelines['Item'])



