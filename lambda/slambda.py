import json
#import boto3
import datetime


def lambda_handler(event, context, pipelines):

   source = event['source'] if event else event
   if source == 'aws.codepipeline':
      pipelines=create_estrutura(event,pipelines)
      pipelines=add_pipeline(event,pipelines)
      pipelines=add_stages(event,pipelines)


#   source = context['source'] if context else context
#   if source == "aws.codepipeline" or source == 'aws.codecommit':
   pipelines=add_logs(event,pipelines)


   return pipelines

def create_estrutura(event,pipeline):
   if len(event['detail']) == 4 or len(event['detail']) == 8:
      resource_id  = event['resources'][0]
      if not resource_id in pipeline.values():
         pipeline = { "resources" : resource_id, "detail": { "running": [ ] } }
   return pipeline

def add_pipeline(event,pipeline):
   if len(event['detail']) == 4:
        execution_id = event['detail']['execution-id']
        running = [running for running in pipeline['detail']['running'] if list(running.keys())[0]==execution_id]
        if running:
           running[0][execution_id]['finished'] = event['time']
           running[0][execution_id]['status']   = event['detail']['state']
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

def add_logs(event,pipeline):
  if isinstance(event,dict) and event:
     if len(event['detail']) == 16 or len(event['detail']) == 13:
        account      =  event['detail']['userIdentity']['accountId']
        source       =  event['source'].split('.')[1]
        region       =  event['region']

        if event['source'] == 'aws.codepipeline':
           name         =  event['detail']['requestParameters']['name']
           resource_id  =  "arn:aws:{0}:{1}:{2}:{3}".format(source,region,account,name)
           execution_id = event['detail']['responseElements']['pipelineExecutionId']

           running = [running for running in pipeline['detail']['running'] if list(running.keys())[0]==execution_id]
           if running:
              running[0][execution_id]['log'] = event

        elif event['source'] == 'aws.codecommit':
             name         =  event['detail']['requestParameters']['s3Key'].split('/')[0]
             resource_id  =  "arn:aws:{0}:{1}:{2}:{3}".format(source,region,account,name)
             print(event)

  return pipeline