'''
file: save_pipeline_in_dynamodb.py
descricao: Script para salvar a estrutura da Pipeline no dynamodb, substituindo o lambda durante
           o desenvolvimento.
autor: Clodonil Honorio Trigo
email: clodonil@nisled.org
data: 27 de abril de 2019
'''

import boto3
import json

    
def create_table(dy,name):
    table     = dy.create_table(
    TableName=name,
    KeySchema=[
        {
            'AttributeName': 'id',
            'KeyType': 'HASH'  #Partition key
        }
    ],
    AttributeDefinitions=[
        {
            'AttributeName': 'id',
            'AttributeType': 'S'
        }
    ],
    ProvisionedThroughput={
        'ReadCapacityUnits': 1,
        'WriteCapacityUnits': 1
    }
    )
    return table.table_status

def delete_table(dy,table):
    dy = boto3.resource('dynamodb', region_name='us-west-1', endpoint_url="http://localhost:8000")
    tb = dy.Table(table)
    tb.delete()

def query_dynamodb(table,id):
    table = dydb.Table(table_name)
    item = table.get_item(Key= { 'id' : id })
    return item

def update(table,resource_id, pipeline):
    table.update_item(Key={'id' :resource_id},
                      UpdateExpression="set detail = :a",
                      ExpressionAttributeValues={':a': pipeline['detail']},      
                      ReturnValues="UPDATED_NEW"
                      )

def search(id):
    item = table.get_item(Key= { 'id' : id })
    return item

if __name__ == '__main__':    
   dydb  = boto3.resource('dynamodb', region_name='us-west-1', endpoint_url="http://localhost:8000")
   table_name = 'code-metrics'
   table = dydb.Table(table_name)

   with open('pipeline2.txt') as json_file:  
      pipeline = json.load(json_file)

   id = 'arn:aws:codepipeline:us-east-1:3422334324:Homolog'
   
   
   

   update(table,id,pipeline)
   print(json.dumps(search(id), indent=4, sort_keys=True))

   #print("Deletando a tabela:", table_name)
   #delete_table(dydb,table_name) 
   
   
   #print("Criando a tabela:", table_name)
   #create_table(dydb,table_name)
   #table.put_item(Item=pipeline)
   #print(query_dynamodb(dydb,pipeline['id'])) 
    
