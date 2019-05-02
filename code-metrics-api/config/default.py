#config default
import os

# port 
PORT = 8080

#DynamoDB
TABLE_NAME=os.environ['DYNAMODB_TABLE']
