from codemetricslambda import CodeMetricsLambda
import pytest


def test_success_dynamodb():
    dynamo_table  = 'pipelines'
    dynamo_region = 'us-east-1'
    sqs_fila      = 'codemetrics'
    sqs_region    = 'us-east-1'

    x = CodeMetricsLambda(dynamo_table, dynamo_region, sqs_fila, sqs_region)
    assert x.conn_dynamodb(dynamo_table, dynamo_region)

def test_not_file_sqs():
    dynamo_table  = 'pipeliness'
    dynamo_region = 'us-east-1'
    sqs_fila      = 'kkkkkk'
    sqs_region    = 'us-east-1'
    x = CodeMetricsLambda(dynamo_table, dynamo_region, sqs_fila, sqs_region)
    assert x.conn_sqs(sqs_fila, sqs_region) == False

def test_success_sqs():
    dynamo_table  = 'pipelines'
    dynamo_region = 'us-east-1'
    sqs_fila      = 'codemetrics'
    sqs_region    = 'us-east-1'
    x = CodeMetricsLambda(dynamo_table, dynamo_region, sqs_fila, sqs_region)
    assert x.conn_sqs(sqs_fila, sqs_region)

def test_load_daddos():
    dynamo_table  = 'pipelines'
    dynamo_region = 'us-east-1'
    sqs_fila      = 'codemetrics'
    sqs_region    = 'us-east-1'
    x = CodeMetricsLambda(dynamo_table, dynamo_region, sqs_fila, sqs_region)
    fila = x.conn_sqs(sqs_fila, sqs_region)
    assert len(x.load_sqs(fila,5)) > 0