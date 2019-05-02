#config staging
import os

REGION_NAME  = os.environ['AWS_REGION']
ENDPOINT_URL = os.environ['DYNAMODB']
ACCESS_ID    = os.environ['AWS_ACCESS_ID']
ACCESS_KEY   = os.environ['AWS_SECRET_KEY']
