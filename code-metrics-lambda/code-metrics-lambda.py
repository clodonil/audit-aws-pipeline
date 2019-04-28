import json
import boto3
import datetime


def lambda_handler(event, context):
    
    print("Event:",event)
    print("Context:",event)
    
    dydb = boto3.resource('dynamodb')
    table = dydb.Table('auditpipelines')
    item = {}
    
    if isinstance(context,dict):
       account      =  context['detail']['userIdentity']['accountId']
       source       =  context['source'].split('.')[1]
       name         =  context['detail']['requestParameters']['name']
       region       =  context['region']
       resource_id  =  "arn:aws:{0}:{1}:{2}:{3}".format(source,region,account,name)
    elif isinstance(event,dict):
       resource_id = event['resources'][0]
       
    item = table.get_item(Key= { 'id' : resource_id })
    
    if 'Item' in item:
       pipelines = { 'id': resource_id, 'detail': item['Item']['detail'] }
    else:    
       pipelines={}
         
    pipelines=create_estrutura(event,pipelines)
    pipelines=add_pipeline(event,pipelines)
    pipelines=add_stages(event,pipelines)
    pipelines=add_logs(context,pipelines)

    
    if 'Item' in item:
             table.update_item(Key={'id' :resource_id},
                      UpdateExpression="set detail = :a",
                      ExpressionAttributeValues={':a': pipelines['detail']},      
                      ReturnValues="UPDATED_NEW"
                      )
    else:    
             estrutura={'id':resource_id,'detail': pipelines['detail']}
             table.put_item(Item=estrutura)
    
    
    
    
def create_estrutura(event,pipeline):
   resource_id  = event['resources'][0]
   if not resource_id in pipeline.values():
      pipeline = {
          "resources" : resource_id,
          "detail": {
          "running": [ ]
          }
      }
   return pipeline

def add_pipeline(event,pipeline):
   if len(event['detail']) == 4:
        execution_id = event['detail']['execution-id']
        running = [running for running in pipeline['detail']['running'] if list(running.keys())[0]==execution_id]
        if running:
           running[0][execution_id]['finished']  = event['time']
           running[0][execution_id]['status']    = event['detail']['state']
           pipeline['detail']['pipeline_status'] = event['detail']['state']
        else:
           account        = event['account']
           start_pipeline = event['time']
           provider       = event['source']
           running  = {}
           running = { execution_id : { 'source': provider, 'account': account, 'start': start_pipeline, 'stages':[] } }
           pipeline['detail']['running'].append(running)

   return pipeline



def add_stages(event,pipeline):
  if len(event['detail']) == 8:
     execution_id = event['detail']['execution-id']
     stage        = event['detail']['stage']
     running = [running for running in pipeline['detail']['running'] if list(running.keys())[0]==execution_id]
     if running:
        stages = [stages for stages in running[0][execution_id]['stages'] if list(stages.keys())[0] == stage]
        if stages:
           inicio = datetime.datetime.strptime(stages[0][stage]['start'],'%Y-%m-%dT%H:%M:%SZ')
           fim    = datetime.datetime.strptime(event['time'],'%Y-%m-%dT%H:%M:%SZ')
           start =  stages[0][stage]['start']
           if inicio < fim:
              stages[0][stage]['status']   = event['detail']['state']
              stages[0][stage]['finished']   = event['time']
           else:
              stages[0][stage]['start']     =  event['time']
              stages[0][stage]['finished']  = start


        else:
            stg = {}
            stg[stage] = {}
            stg[stage]['provider']    = event['detail']['type']['provider']
            stg[stage]['status']      = event['detail']['state']
            stg[stage]['start']       = event['time']
            stg[stage]['eventid']     = event['id']
            stg[stage]['output']      = []
            stg[stage]['execute']     = []
            running[0][execution_id]['stages'].append(stg)

  return pipeline

def add_logs(context,pipeline):
  if isinstance(context,dict):
     print(context)
     if len(context['detail']) == 13:
        account      =  context['detail']['userIdentity']['accountId']
        source       =  context['source'].split('.')[1]
        name         =  context['detail']['requestParameters']['name']
        region       =  context['region']
        resource_id  =  "arn:aws:{0}:{1}:{2}:{3}".format(source,region,account,name)
        execution_id = context['detail']['responseElements']['pipelineExecutionId']

        if context['source'] == 'aws.codepipeline':
           running = [running for running in pipeline['detail']['running'] if list(running.keys())[0]==execution_id]
           running[0][execution_id]['log'] = context

  return pipeline
