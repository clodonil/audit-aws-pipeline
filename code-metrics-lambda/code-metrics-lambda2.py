import boto3
import botocore
import datetime
import json
import copy
import time
import os

def lambda_handler(event, context):
    codemetrics =  CodeMetricsLambda()
    codemetrics.running()
    

class CodeMetricsLambda:
    def __init__(self):
        self.sqs_fila   = 'codemetrics'
        self.sqs_region = 'sa-east-1'

        self.dytbmetricas  = 'codemetrics-metricas'
        self.dytbdetail    = 'codemetrics-pipelines'
        self.tbmetricasraw = 'codemetrics-raw'
        self.dyregion      = 'sa-east-1'

    def conn_dynamodb(self,table,region):
        try:
            dydb = boto3.resource('dynamodb',region_name=region)
            table = dydb.Table(table)
            return table
        except:
            print("Problema na conexao com DynamoDB")
            return False

    def conn_sqs(self,fila,region):
        try:
            sqs = boto3.resource('sqs', region_name=region)
            queue = sqs.get_queue_by_name(QueueName=fila)
            return queue
        except:
            print("Problema na conexao com o sqs")
            return False

    def load_sqs(self,conn):
        event = []
        semafaro = True

        while semafaro and len(event) < 600:
            messages = conn.receive_messages(MaxNumberOfMessages=10, AttributeNames=['All'], WaitTimeSeconds=1)

            if not messages:
                semafaro = False
            else:
                for item in messages:
                    event.append(item)

        return event

    def event_pipeline(self,item):
        event = {'detail': []}
        try:
           event = json.loads(item.body)
        except:
           print("Problema para obter item da lista")
           print(item.body)
           
        countreceive = item.attributes['ApproximateReceiveCount'] 
        return event,countreceive

    def get_header(self,event):
        header = {}
        if len(event['detail']) in [4,5,6,8]:
            header['execution_id'] = event['detail']['execution-id']
            header['length']       = len(event['detail'])
            header['resource_id']  = event['resources'][0]
            header['account']      = event['account']
        else:
            header['length']       = len(event['detail'])

        return header

    def nova_pipeline(self,pipelinedb):
        if 'Item' in pipelinedb:
            return False
        else:
            return True

    def proc_events(self, conn_sqs,tbmetricas, tbdetail,tbraw):
        sqs_file = self.load_sqs(conn_sqs)
        semafaro = 0
        while semafaro < 2 and len(sqs_file) != 0:   
            for item  in sqs_file:
                
                print("Items", len(sqs_file))
                print("Semafaro:", semafaro )
                

                # change string in json
                event,countreceive = self.event_pipeline(item)
                
                # contrala se o evento foi usado
                used = False

                #get header do json
                header = self.get_header(event)

                # Recupera a pipeline salva no dynamodb
                if header['length'] in [4,5,6,8]:
                    query = { 'id' : header['resource_id'], 'running' : header['execution_id'] }
                    pipelinedb   = self.dynamodb_query(tbdetail,query)
                    pipelineold  = copy.deepcopy(pipelinedb)
                    pipelines    = {}

                    if self.nova_pipeline(pipelinedb):
                        if header['length'] == 4:
                            used, pipelines = self.create_pipeline(event)
                            if pipelines:
                                self.save_pipeline(pipelinedb,pipelines,tbdetail,header['execution_id'])
                                # Registrando o catalogo
                                key= { 'account' : header['account'], 'resource_id': header['resource_id'] }
                                lista_pipelines = self.dynamodb_query(tbmetricas,key)
                                if self.nova_pipeline(lista_pipelines):
                                   catalogo = self.registra_catalogo()
                                   dados    = {'account': header['account'], 'resource_id': header['resource_id'],'detail': catalogo }
                                   self.dynamodb_save_metrics(tbmetricas, header['account'] ,header['resource_id'], dados, True)
                    else:
                        pipelines = { 'id': header['resource_id'], 'running':header['execution_id'], 'detail': pipelinedb['Item']['detail'] }

                        # create e update pipeline
                        if header['length'] == 4:
                            used,pipelines = self.finished_pipeline(event,pipelines)

                        # create e update stages
                        elif header['length'] == 5:
                            if self.exist_pipeline(pipelines):
                                used, pipelines=self.stages(event,pipelines)
                                
                        # update type of pipeline
                        elif header['length'] == 6:
                           if self.exist_pipeline(pipelines):
                                used, pipelines=self.popula(event,pipelines)
                        
                        # create e update action
                        elif header['length'] == 8:
                            if self.exist_stage(event,pipelines):
                                used, pipelines=self.actions(event,pipelines)

                    #if self.item_used(pipelineold,pipelines):
                    if used:
                        if self.save_pipeline(pipelinedb, pipelines,tbdetail,header['execution_id']):
                            if self.pipeline_completed(pipelines):
                                # Salva as metricas da pipeline
                                self.salve_metrics(pipelines,tbmetricas, header['account'])
                            if self.sqs_delete_item(item):
                                sqs_file.remove(item)
                                used = True
                                msg="{0} deletado da Fila SQS e Incluido no DynamoDB".format(header['execution_id'])
                                print(msg)
                    elif int(countreceive) > 100:
                        if self.sqs_delete_item(item):
                            sqs_file.remove(item)
                       

                elif header['length'] == 13:
                    dados = {'id':event['id'],'detail':event}
                    #if self.dynamodb_save(tbraw, dados, True):
                    self.sqs_delete_item(item)


            if not used:
                semafaro += 1

        #Salvar aqui

    def saveLog(self,event):
        with open('logs.json', 'a') as json_file:
            json.dump(event, json_file)


    def registra_catalogo(self):

        resource =  { 'pipeline_status' : 'Null',
                      'stages': 'Null',
                      'running':[],
                      'stage-eventid' : [],
                      'action-eventid' : [],
                      'sum_success': '0',
                      'sum_faild':   '0',
                      'stage_faild':{},
                      'action_faild':{},
                      'deploy_day':[],
                      'runtime' : 'Null',
                      'version_pipeline': 'Null',
                      'type':'Null',
                      'time_deploy': '0'
                    }
                  
        return resource

    def item_used(self,pipelinedb,pipelines):
        #Verifica se ouve mudanca na pipeline
        if self.nova_pipeline(pipelinedb):
            old = []
        else:
            old = pipelinedb['Item']['detail']

        if pipelines:
            new = pipelines['detail']
            if old != new:
                return True
            else:
                return False
        else:
            return False

    def sqs_delete_item(self,item):
        retorno = item.delete()
        if retorno['ResponseMetadata']['HTTPStatusCode'] == 200:
            return True
        else:
            return False

    def save_pipeline(self,pipelinedb, pipelines,dytable, running):
        if self.nova_pipeline(pipelinedb):
            dados={'id': pipelines['resources'],'running':running, 'detail': pipelines['detail'] }
            retorno=self.dynamodb_save(dytable,dados,True)

        else:
            dados={'id':pipelines['id'], 'running':running, 'detail': pipelines['detail']}
            retorno=self.dynamodb_save(dytable, dados, False)
        return retorno

    def dynamodb_save(self,table,dados,new):
        retorno= {'ResponseMetadata': {'HTTPStatusCode' : 300    }}
        if new:
            try:
               retorno=table.put_item(Item=dados)
            except botocore.exceptions.ClientError as e:
                print(e)
        else:
            try:
               retorno=table.update_item(Key={'id':dados['id'],'running': dados['running']},
                                      UpdateExpression="set detail = :a",
                                      ExpressionAttributeValues={':a': dados['detail']},
                                      ReturnValues="UPDATED_NEW")
            except botocore.exceptions.ClientError as e:
               print(e)    
                                      
        if retorno['ResponseMetadata']['HTTPStatusCode'] == 200:
            return True
        else:
            return False

    def dynamodb_save_metrics(self,table,account, resource_id, dados, new):
        retorno= {'ResponseMetadata': {'HTTPStatusCode' : 300    }}
        if new:
           try:
              retorno=table.put_item(Item=dados)
           except botocore.exceptions.ClientError as e:
              print(e)    
        else:   
           try:    
              retorno=table.update_item(Key={'account': account, 'resource_id': resource_id},
                                      UpdateExpression="set detail = :a",
                                      ExpressionAttributeValues={':a': dados},
                                      ReturnValues="UPDATED_NEW"
                                      )
           except botocore.exceptions.ClientError as e:
             print(e)    
                                      
        if retorno['ResponseMetadata']['HTTPStatusCode'] == 200:
           return True
        else:
           return False

    def dynamodb_query(self,table,query):
        return table.get_item(Key=query)

    def exist_pipeline(self,pipeline):
        if pipeline:
            return True
        else:
            return False

    def exist_stage(self,event,pipeline):

        stage    = event['detail']['stage']
        stages    = [stages for stages in pipeline['detail']['stages'] if  list(stages.keys())[0]  ==  stage]

        if stages:
            return True
        else:
            return False

    def create_pipeline(self,event):
        used  = False
        state    = event['detail']['state']
        pipeline = {}
        if state == 'STARTED':
            used         = True
            resource_id  = event['resources'][0]
            pipeline = {
                "resources" : resource_id,
                "detail": {
                    "start_pipeline": event['time'],
                    "status"         : event['detail']['state'],
                    "stages"        : [],
                    "provider"      :event['source'],
                    "finished_pipeline": 'Null',
                    "runtime" : "Null",
                    "version_pipeline": "Null",
                    "type":"Null"

                }
            }

        return [used, pipeline]

    def finished_pipeline(self,event,pipeline):
        state = event['detail']['state']
        used  = False
        if state != 'STARTED':
            used  = True
            pipeline['detail']['finished_pipeline'] = event['time']
            pipeline['detail']['status'] = state
        return [used, pipeline]

    def stages(self,event,pipeline):
        stage  = event['detail']['stage']
        state  = event['detail']['state']
        used   = False
        stages = [stages for stages in pipeline['detail']['stages'] if  list(stages.keys())[0]  ==  stage]

        if stages:
            used  = True
            stages[0][stage]['finished']  = event['time']
            stages[0][stage]['status']    = state

        elif state == 'STARTED':
            used  = True
            stg = {}
            stg[stage] = {}
            stg[stage]['status']      = state
            stg[stage]['start']       = event['time']
            stg[stage]['eventid']     = event['id']
            stg[stage]['action']      = []
            stg[stage]['finished']    = "Null"
            pipeline['detail']['stages'].append(stg)

        return [used, pipeline]

    def actions(self,event,pipeline):
        stage  = event['detail']['stage']
        action = event['detail']['action']
        state  = event['detail']['state']
        used   = False

        stages = [stages for stages in pipeline['detail']['stages'] if  list(stages.keys())[0]  ==  stage]
        if stages:
            actions = [actions for actions in stages[0][stage]['action'] if list(actions.keys())[0] == action]
            if actions:
                used  = True
                actions[0][action]['finished']  = event['time']
                actions[0][action]['status']    = state
            elif state == 'STARTED':
                used  = True
                act   = {}
                act[action] = {}
                act[action]['provider']  = event['detail']['type']['provider']
                act[action]['status']    = state
                act[action]['start']     = event['time']
                act[action]['eventid']   = event['id']
                act[action]['finished']  = "Null"
                stages[0][stage]['action'].append(act)

        return [used, pipeline]
        
    def popula(self, event,pipelines):
        used = False
        if 'runtime' in event['detail']:
            if 'runtime' in pipelines['detail']:
                print(event)
                pipelines['detail']['runtime'] = event['detail']['runtime']
                pipelines['detail']['version_pipeline'] = event['detail']['version_pipeline']
                pipelines['detail']['type'] = event['detail']['type']
                used = True
                
        return [used, pipelines]        
        

    def running(self):
        conn = self.conn_sqs(self.sqs_fila, self.sqs_region)
        tbmetricas = self.conn_dynamodb(self.dytbmetricas   , self.dyregion)
        tbdetail   = self.conn_dynamodb(self.dytbdetail     , self.dyregion)
        tbraw      = self.conn_dynamodb(self.tbmetricasraw  , self.dyregion)
        if conn and tbmetricas and tbdetail and tbraw:
            self.proc_events(conn, tbmetricas,tbdetail, tbraw)

    def metrics_faild(self,list_stages):
        """
        Metricas sobre o status da pipeline
        metrics: action_fail, pipeline_status, stage_fail
        """
        fail         = []
        stages_fail  = {}
        actions_fail = {}
        for stages in list_stages:
            for stage in stages.keys():
                if stages[stage]['status'] == 'FAILED':
                    stage_eventid = stages[stage]['eventid']
                    if stage in stages_fail:
                        stages_fail[stage]['numero'] +=1
                    else:
                        stages_fail[stage] = { 'qtd' : 1, 'eventid' : stage_eventid }

                lista_actions = [actions for actions in stages[stage]['action']]
                control_actions = {}
                for actions in lista_actions:
                    for action in actions.keys():
                        if actions[action]['status'] == 'FAILED':
                            action_eventid = actions[action]['eventid']
                            if action in actions_fail:
                                actions_fail[action]['qtd'] +=1
                            else:
                                actions_fail[action] = { 'qtd' : 1, 'eventid' : action_eventid }
        fail.append(stages_fail)
        fail.append(actions_fail)
        return fail

    def metrics_time(self, list_stages, num_execucao):
        """
        Metricas sobre tempo de deploy, stage e action
        metricas: time_deploy, time_stage, time_action
        """
        control_stages = {}
        for stages in list_stages:
            for stage in stages.keys():
                if stages[stage]['status'] == 'SUCCEEDED':
                    time = datetime.datetime.strptime(stages[stage]['finished'],'%Y-%m-%dT%H:%M:%SZ') - datetime.datetime.strptime(stages[stage]['start'],'%Y-%m-%dT%H:%M:%SZ')
                    control_stages[stage] =  {'time': str(self.change_in_segunds(time)/num_execucao),'actions':[]}

                    lista_actions = [actions for actions in stages[stage]['action']]
                    control_actions = {}
                    for actions in lista_actions:
                        for action in actions.keys():
                            if actions[action]['status'] == 'SUCCEEDED':
                                action_time = datetime.datetime.strptime(actions[action]['finished'],'%Y-%m-%dT%H:%M:%SZ') - datetime.datetime.strptime(actions[action]['start'],'%Y-%m-%dT%H:%M:%SZ')
                                control_actions[action] = {'time': str(self.change_in_segunds(action_time)/num_execucao)}

                    control_stages[stage]['actions'].append(control_actions)

        return control_stages

    def change_in_segunds(self,hora):
        """
        Transforma hora em string para segundos
        """
        #hora,min,seg = str(hora).split(":")
        #segunds = (int(min)*60) + (int(hora)*120) + int(float(seg))
        segunds = hora.total_seconds()
        return segunds

    def pipeline_completed(self,pipeline):
        """
        Verifica se a pipeline esta finalizada, para pegar as metricas
        """
        # tempo final
        completed = True
        stages =  [stages for stages in pipeline['detail']['stages']]
        if pipeline['detail']['finished_pipeline'] != 'Null' and pipeline['detail']['finished_pipeline'] != 'Null'and stages:
            for stage in stages:
                for stage_name in stage.keys():
                    actions = [actions for actions in stage[stage_name]['action']]
                    for action in actions:
                        for action_name in action:
                            if action[action_name]['finished'] == 'Null':
                                completed = False
                                break
                    if stage[stage_name]['finished'] == 'Null' or not actions:
                        completed = False
                        break
        else:
            completed = False

        return completed

    def salve_metrics(self, pipeline, tbmetricas, account):
        """
        Salva as metricas da pipeline
        """
        arn = pipeline['id']
        key = { 'account' : account, 'resource_id': arn }
        dynamo_carga    = self.dynamodb_query(tbmetricas,key)
        dynamo_metrics  = dynamo_carga['Item']['detail']
        pipeline_status = pipeline['detail']['status']
        
        if 'runtime' in pipeline['detail']:
           print(pipeline)
           print(dynamo_metrics)
           dynamo_metrics['runtime'] = pipeline['detail']['runtime']
           dynamo_metrics['version_pipeline'] = pipeline['detail']['version_pipeline']
           dynamo_metrics['type'] = pipeline['detail']['type']


        if not pipeline['running'] in dynamo_metrics['running']:
            dynamo_metrics['running'].append(pipeline['running'])
            sum_success = int(dynamo_metrics['sum_success'])
            sum_faild   = int(dynamo_metrics['sum_faild'])
            if pipeline_status == 'SUCCEEDED':
                sum_success += 1
                time_deploy  = datetime.datetime.strptime(pipeline['detail']['finished_pipeline'],'%Y-%m-%dT%H:%M:%SZ') - datetime.datetime.strptime(pipeline['detail']['start_pipeline'] ,'%Y-%m-%dT%H:%M:%SZ')
                dynamo_metrics['time_deploy'] = str(self.change_in_segunds(time_deploy))
                data = pipeline['detail']['finished_pipeline'].split('T')[0]
                deploy_day = [x for x in dynamo_metrics['deploy_day'] if list(x.keys())[0] == data]
                if deploy_day:
                   deploy_day[0][data] = str(int(deploy_day[0][data]) + 1)
                else:
                   dynamo_metrics['deploy_day'].append({data:'1'})


            elif pipeline_status == 'FAILED':
                sum_faild   += 1
            dynamo_metrics['sum_success']     = str(sum_success)
            dynamo_metrics['sum_faild']       = str(sum_faild)

        stages  =  [stages for stages in pipeline['detail']['stages']]
        if pipeline_status == 'SUCCEEDED':
            dynamo_metrics['pipeline_status'] = 1

        elif pipeline_status == 'FAILED':
            dynamo_metrics['pipeline_status'] = 0

            fail    = self.metrics_faild(stages)
            fail_stages  = fail[0]
            fail_actions = fail[1]

            print(fail_stages)
            print(fail_actions)
            
            for f_stages in fail_stages:
                if not fail_stages[f_stages]['eventid'] in dynamo_metrics['stage-eventid']:
                   dynamo_metrics['stage-eventid'].append(fail_stages[f_stages]['eventid'])    
                   if f_stages in dynamo_metrics['stage_faild']:
                      dynamo_metrics['stage_faild'][f_stages] = str(int(dynamo_metrics['stage_faild'][f_stages]) + int(fail_stages[f_stages]['qtd']))
                   else:
                      dynamo_metrics['stage_faild'][f_stages] = str(fail_stages[f_stages]['qtd'])

            for f_actions in fail_actions:
                if not fail_actions[f_actions]['eventid'] in dynamo_metrics['action-eventid']:
                   dynamo_metrics['action-eventid'].append(fail_actions[f_actions]['eventid'])        
                   if f_actions in dynamo_metrics['action_faild']:
                      dynamo_metrics['action_faild'][f_actions] = str(int(dynamo_metrics['action_faild'][f_actions]) + int(fail_actions[f_actions]['qtd']))
                   else:
                      dynamo_metrics['action_faild'][f_actions] = str(fail_actions[f_actions]['qtd'])

        metrics = self.metrics_time(stages, len(dynamo_metrics['running']) )
        dynamo_metrics['stages'] = metrics
        retorno = self.dynamodb_save_metrics(tbmetricas, account ,arn, dynamo_carga['Item']['detail'], False)
        return retorno

