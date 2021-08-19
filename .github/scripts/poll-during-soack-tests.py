import time
import argparse

# Sleep while `docker-compose.yml` starts up
sleep(3s)

# $1 - ${{ env.HOSTMETRICS_COLLECTION_INTERVAL_IN_SECONDS }}

# Create CloudWatch Alarms for CPU Load & Memory Usage

# While docker-compose is still running, check the alarms
while [ $(pgrep docker-compose) ];
do
    echo 'Soak Tests still running';
    
    # If the alarms failed, fail this script and exit this for loop
    # if [ aws cloudwatch describe-alarms ]
    #     echo 'Failed with: ';
    #     echo "::set-output name=FAILED_DURING_SOAK_TESTS::True"
    #     exit 1;
    # fi;

    # Sleep until hostmetrics has a chance to post more metrics, get the period as an input
    sleep($1s)
done

# ALWAYS terminate the docker-compose after the script ends

print('Done checking for alarms.')