import boto3
import json
import copy
import time

class CodeMetricsLambda:
    def __init__(self,dynamo_table, dynamo_region, sqs_fila, sqs_region):
        self.dynamo_table  = dynamo_table
        self.dynamo_region = dynamo_region
        self.sqs_fila      = sqs_fila
        self.sqs_region    = sqs_region

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
            print("Problema na connexao com o sqs")
            return False

    def load_sqs(self,conn):
        event = []
        semafaro = True

        while semafaro:
           messages = conn.receive_messages(MaxNumberOfMessages=10, AttributeNames=['All'], WaitTimeSeconds=1)

           if not messages:
              semafaro = False
           else:
             for item in messages:
                 event.append(item)

        return event

    def event_pipeline(self,item):
        event = json.loads(item.body)
        return event

    def get_header(self,event):
        header = {}
        if len(event['detail']) in [4,5,8]:
            header['execution_id'] = event['detail']['execution-id']
            header['length']       = len(event['detail'])
            header['resource_id']  = event['resources'][0]
        else:
            header['execution_id'] = event['detail']['responseElements']['pipelineExecutionId']
            header['length']       = len(event['detail'])
            account                =  event['detail']['userIdentity']['accountId']
            source                 =  event['source'].split('.')[1]
            name                   =  event['detail']['requestParameters']['name']
            region                 =  event['region']
            resource_id            =  "arn:aws:{0}:{1}:{2}:{3}".format(source,region,account,name)
            header['resource_id']  = resource_id

        return header

    def nova_pipeline(self,pipelinedb):
        if 'Item' in pipelinedb:
            return False
        else:
            return True

    def proc_events(self, dytable,conn_sqs):

        sqs_file = self.load_sqs(conn_sqs)

        semafaro = True

        while semafaro:
            semafaro = False
            lista_item_salvos = []

            for item  in sqs_file:
                # change string in json
                event  = self.event_pipeline(item)

                #get header do json
                header = self.get_header(event)

                query = { 'id' : header['resource_id'] }
                # Recupera a pipeline salva no dynamodb
                if header['length'] in [4,5,8,13]:
                    pipelinedb   = self.dynamodb_query(dytable,query)
                    pipelineold  = copy.deepcopy(pipelinedb)

                    if self.nova_pipeline(pipelinedb):
                        if header['length'] == 4:
                            pipelines=self.create_estrutura(event)
                            self.save_pipeline(pipelinedb, pipelines,dytable)

                            # Registrando o catalogo
                            key= { 'id' : 'pipelines' }
                            lista_pipelines = self.dynamodb_query(dytable,key)
                            catalogo        = self.registra_catalogo(lista_pipelines, event['account'], header['resource_id'])
                            self.dynamodb_save(dytable, catalogo, key)
                    else:
                        pipelines    = { 'id': header['resource_id'], 'detail': pipelinedb['Item']['detail'] }

                        # create e update pipeline
                        if header['length'] == 4:
                            pipelines = self.create_pipeline(event,pipelines)

                        # create e update stages
                        elif header['length'] == 5:
                            if self.exist_pipeline(header['execution_id'],pipelines):
                                pipelines=self.stages(event,pipelines)

                        # create e update action
                        elif header['length'] == 8:
                            if self.exist_stage(event,pipelines):
                                pipelines=self.actions(event,pipelines)

                        elif header['length'] == 13:
                            if self.exist_pipeline(header['execution_id'],pipelines):
                                pipelines = self.pipelineLog(header,event,pipelines)

                        if self.item_usage(pipelineold,pipelines):
                            if self.save_pipeline(pipelinedb, pipelines,dytable):
                                if self.sqs_delete_item(item):
                                    lista_item_salvos.append(item)
                                    msg="{0} deletado da Fila SQS e Incluido no DynamoDB".format(header['execution_id'])
                                    print(msg)
                                    # self.saveLog(event)
            for item in lista_item_salvos:
                sqs_file.remove(item)
                semafaro = True

        #Salvar aqui

    def saveLog(self,event):
        with open('logs.json', 'a') as json_file:
            json.dump(event, json_file)

    def nova_conta_catalogo(self, account, catalogo):
        if account in catalogo:
            return False
        else:
            return True

    def registra_catalogo(self,lista_pipelines, account, resource_id):
        catalogo = {account : [resource_id]}
        if not self.nova_pipeline(lista_pipelines):
            catalogo = lista_pipelines['Item']['detail']
            if not self.nova_conta_catalogo(account,catalogo):
                if not resource_id in catalogo[account]:
                    catalogo[account].append(resource_id)
            else:
                catalogo[account] = [resource_id]
        return catalogo

    def item_usage(self,pipelinedb,pipelines):
        #Verifica se ouve mudanca na pipeline
        if self.nova_pipeline(pipelinedb):
            old = []
        else:
            old = pipelinedb['Item']['detail']
        new = pipelines['detail']

        if old != new:
            return True
        else:
            return False

    def sqs_delete_item(self,item):
        retorno = item.delete()
        if retorno['ResponseMetadata']['HTTPStatusCode'] == 200:
            return True
        else:
            return False

    def save_pipeline(self,pipelinedb, pipeline,dytable):
        if self.nova_pipeline(pipelinedb):
            key={'id': pipeline['resources']}
            retorno = self.dynamodb_save(dytable, pipeline['detail'], key)
        else:
            estrutura={'id':pipeline['id'],'detail': pipeline['detail']}
            retorno=self.dynamodb_save(dytable, estrutura, False)
        return retorno

    def dynamodb_save(self,table,pipeline,estrutura):
        if estrutura:
            estrutura['detail'] = pipeline
            retorno=table.put_item(Item=estrutura)
        else:
            retorno=table.update_item(Key={'id':pipeline['id']},
                                      UpdateExpression="set detail = :a",
                                      ExpressionAttributeValues={':a': pipeline['detail']},
                                      ReturnValues="UPDATED_NEW"
                                      )
        if retorno['ResponseMetadata']['HTTPStatusCode'] == 200:
            return True
        else:
            return False

    def dynamodb_query(self,table,query):
        return table.get_item(Key=query)

    def exist_pipeline(self,execution_id,pipeline):
        running = [running for running in pipeline['detail']['running'] if list(running.keys())[0]==execution_id]
        if running:
            return True
        else:
            return False

    def exist_stage(self,event,pipeline):
        execution_id =  event['detail']['execution-id']
        stage        = event['detail']['stage']
        running = [running for running in pipeline['detail']['running'] if list(running.keys())[0]==execution_id]
        if running:
            stages = [stages for stages in running[0][execution_id]['stages'] if list(stages.keys())[0] == stage]
            if stages:
                return True
            else:
                return False

    def create_estrutura(self,event):
        resource_id  = event['resources'][0]
        pipeline = {
            "resources" : resource_id,
            "detail": {
                "running": [ ]
            }
        }
        return pipeline

    def create_pipeline(self,event,pipeline):
        execution_id = event['detail']['execution-id']
        state        = event['detail']['state']
        running = [running for running in pipeline['detail']['running'] if list(running.keys())[0]==execution_id]
        if running:
            running[0][execution_id]['finished']  = event['time']
            running[0][execution_id]['status']    = state
            pipeline['detail']['pipeline_status'] = event['detail']['state']
        elif state == 'STARTED':
            account        = event['account']
            start_pipeline = event['time']
            provider       = event['source']
            running  = {}
            running  = { execution_id : { 'source': provider, 'account': account, 'start': start_pipeline, 'stages':[] } }
            pipeline['detail']['running'].append(running)
        return pipeline

    def pipelineLog(self,header,event,pipeline):

        execution_id = header['execution_id']
        running = [running for running in pipeline['detail']['running'] if list(running.keys())[0]==execution_id]
        if running:
            running[0][execution_id]['logs'] = event

        return pipeline

    def stages(self,event,pipeline):
        execution_id = event['detail']['execution-id']
        stage        = event['detail']['stage']
        state        = event['detail']['state']
        running = [running for running in pipeline['detail']['running'] if list(running.keys())[0]==execution_id]
        if running:
            stages = [stages for stages in running[0][execution_id]['stages'] if list(stages.keys())[0] == stage]

            if not stages:
                if state == 'STARTED':
                    stg = {}
                    stg[stage] = {}
                    stg[stage]['status']      = state
                    stg[stage]['start']       = event['time']
                    stg[stage]['action']      = []
                    stg[stage]['finished']    = "Null"
                    running[0][execution_id]['stages'].append(stg)
            else:
                stages[0][stage]['finished']  = event['time']
                stages[0][stage]['status']    = state

        return pipeline

    def actions(self,event,pipeline):
        execution_id = event['detail']['execution-id']
        stage        = event['detail']['stage']
        action       = event['detail']['action']
        state        = event['detail']['state']
        running = [running for running in pipeline['detail']['running'] if list(running.keys())[0]==execution_id]
        if running:
            stages = [stages for stages in running[0][execution_id]['stages'] if list(stages.keys())[0] == stage]
            if stages:
                actions = [actions for actions in stages[0][stage]['action'] if list(actions.keys())[0] == action]
                if not actions:
                    if state == 'STARTED':
                        act = {}
                        act[action] = {}
                        act[action]['provider']  = event['detail']['type']['provider']
                        act[action]['status']    = state
                        act[action]['start']     = event['time']
                        act[action]['eventid']   = event['id']
                        act[action]['logs']      = []
                        act[action]['finished']  = "Null"
                        stages[0][stage]['action'].append(act)
                else:
                    actions[0][action]['finished']  = event['time']
                    actions[0][action]['status']    = state
        return pipeline

    def running(self):
        dytable = self.conn_dynamodb(self.dynamo_table, self.dynamo_region)
        conn = self.conn_sqs(self.sqs_fila, self.sqs_region)
        if dytable and conn:
           self.proc_events(dytable, conn)




#
#from codemetricslambda import CodeMetricsLambda

#dynamo_table  = 'codemetrics'
#dynamo_region = 'sa-east-1'
#sqs_fila      = 'codemetrics'
#sqs_region    = 'sa-east-1'

#x = CodeMetricsLambda(dynamo_table, dynamo_region, sqs_fila, sqs_region)

#x.running()

#print('finalizado')