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

    failure = False
    if len(met['running']) != (int(met['sum_faild']) + int(met['sum_success']))  : failure = True

    if failure:
        print(json.dumps(met, indent=4, sort_keys=True))



metricas = getpipelines()
for metrica in metricas:
    falha_estrutura(metrica['detail'])