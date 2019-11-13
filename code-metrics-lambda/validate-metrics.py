'''
Script para validar se os dados gravados no Dynamodb estão com a estrutura correta
'''

import datetime
import boto3
import json

def getpipelines():
    table = 'codemetrics-metricas'
    client = boto3.resource('dynamodb',region_name='sa-east-1')
    table = client.Table(table)
    retorno = table.scan()
    return retorno['Items']


def falha_estrutura(met):

    # Verifica o total de execucao com o total x sucesso e falhas
    failure = False
    if len(met['running']) != (int(met['sum_faild']) + int(met['sum_success']))  : failure = True
    
    # Total de Deploy tem que ser menor que o numero de execucao
    total_deploy = 0
    for  days in met["deploy_day"]:
      for day in days:
          total_deploy += int(days[day])

    if len(met['running']) < total_deploy  : failure = True
    
    # Total de deploy tem que ser igual ao numero de sucesso
    if total_deploy != int(met['sum_success']) : failure = True
    
    action_falha = 0
    for action in met['action_faild']:
        action_falha += int(met['action_faild'][action])
        
    stage_falha = 0
    for stage in met['stage_faild']:
        stage_falha += int(met['stage_faild'][stage])
    
    # Total de falhar em action tem que ser no stage
    if stage_falha != action_falha :  failure = True
    

    return failure

metricas = getpipelines()
for metrica in metricas:
    if falha_estrutura(metrica['detail']):
        print(metrica['resource_id'])
    
print("FIM")