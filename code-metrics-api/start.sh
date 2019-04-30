#!/bin/bash
# start.sh

dir=$(pwd)
export APP_CONFIG_FILE="$dir/config/staging.py"
python3 run.py