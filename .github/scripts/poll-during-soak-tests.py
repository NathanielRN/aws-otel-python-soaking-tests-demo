import argparse
import json
import logging
import os
import sys
import time

import docker

logging.basicConfig(level=logging.INFO)

logger = logging.getLogger(__file__)

LOAD_GENERATOR_CONTAINER_NAME = "app-collector-combo_generate-load_1"
SOAK_TESTS_STARTED_TIMEOUT = 10


def parse_args():
    parser = argparse.ArgumentParser(
        description="""
        poll-during-soak-tests.py continuously polls the backend monitoring tool
        to see if an alarm has triggered because of a spike in the Soak Tests.
        """
    )

    parser.add_argument(
        "--polling-interval",
        required=True,
        type=int,
        help="""
        The interval with which the script polls the Soak Test alarms.
        In seconds.

        Examples:

            --polling-interval=600
        """,
    )

    return parser.parse_args()


if __name__ == "__main__":
    logger.debug("Starting Alarm Polling Script.")

    args = parse_args()

    start = time.time()

    docker_client = docker.from_env()

    print("Currently running containers: ", [c.name for c in docker_client.containers.list(filters={"status": "running"})])
    while LOAD_GENERATOR_CONTAINER_NAME not in [c.name for c in docker_client.containers.list(filters={"status": "running"})]:
        logger.info("Load Generator container has not started.")
        if time.time() - start > SOAK_TESTS_STARTED_TIMEOUT:
            logger.error(
                "Soak Tests docker container process did not start after %s seconds",
                SOAK_TESTS_STARTED_TIMEOUT,
            )
            sys.exit(1)
        print("Currently running containers: ", [c.name for c in docker_client.containers.list(filters={"status": "running"})])
        time.sleep(1)

    did_soak_test_fail_during = False

    while (
        docker_client.containers.get(
            LOAD_GENERATOR_CONTAINER_NAME
        ).attrs["State"]["Status"]
        == "running"
    ):
        alarms_info = json.loads(
            os.popen(
                "aws cloudwatch describe-alarms --alarm-name-prefix 'OTel Python Soak Tests - '"
            ).read()
        )

        for alarm in alarms_info["MetricAlarms"]:
            if alarm["StateValue"] == "ALARM":
                logger.error(
                    "Triggered alarm %s with reason: %s",
                    alarm["AlarmName"],
                    alarm["StateReason"],
                )
                did_soak_test_fail_during = True
            logger.info(
                "Alarm %s was %s", alarm["AlarmName"], alarm["StateValue"]
            )

        time.sleep(args.polling_interval)

    for container in docker_client.containers.list(
        filters={"status": "running"}
    ):
        container.stop()

    if did_soak_test_fail_during:
        logger.error(
            "Failing because of alarms triggered during Soak Test. Dumping logs: %s",
            {
                "app": docker_client.containers.get(
                    "app-collector-combo_app_1"
                ).logs(),
                "collector": docker_client.containers.get(
                    "app-collector-combo_otel_1"
                ).logs(),
                "load_generator": docker_client.containers.get(
                    LOAD_GENERATOR_CONTAINER_NAME
                ).logs(),
            },
        )
        sys.exit(2)

    logger.info("Done polling Soak Test alarms.")
