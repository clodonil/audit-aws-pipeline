#!/bin/bash


echo "Executando o Setup: Criando Role, DynamoDB, SQS"




echo "Criando Lambda"

zip codemetric-lambda-$VERSION.zip lambda.py 
 
aws s3 cp codemetric-lambda-$VERSION.zip s3://$S3Bucket/codemetric-lambda-$VERSION.zip 
aws cloudformation deploy --stack-name codemetrics-lambda-deploy 
                          --template-file lambda.yml 
                          --parameter-overrides CodeS3Name=codemetric-lambda-$VERSION.zip S3Bucket=$S3Bucket 
                          --capabilities CAPABILITY_NAMED_IAM 

 