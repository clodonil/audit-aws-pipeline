# start.sh

dir=$(pwd)
export APP_CONFIG_FILE=/home/clodonil/Workspace/audit-aws-pipeline/code-metrics-api/config/staging.py
echo $APP_CONFIG_FILE
python3 run.py