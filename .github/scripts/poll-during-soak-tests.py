import argparse
import json
import logging
import os
import sys
import time

import docker
import psutil
from psutil import NoSuchProcess

logging.basicConfig(level=logging.INFO)

logger = logging.getLogger(__file__)

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

    soak_tests_docker_compose_process: psutil.Process = None
    while not soak_tests_docker_compose_process:
        try:
            for process in psutil.process_iter():
                if process.name() == "docker-proxy":
                    soak_tests_docker_compose_process = process
                    logger.info("Found matching process: %s", str(process))
                    break
        except NoSuchProcess as exc:
            pass
        if time.time() - start > SOAK_TESTS_STARTED_TIMEOUT:
            logger.error(
                "Soak Tests `docker-proxy` process did not start after %s seconds",
                SOAK_TESTS_STARTED_TIMEOUT,
            )
            sys.exit(1)

    did_soak_test_fail_during = False

    docker_client = docker.DockerClient(base_url="unix://var/run/docker.sock")

    while (
        docker_client.containers.get("app-collector-combo_generate-load").attrs[
            "State"
        ]["Status"]
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

    for container_name in docker_client.containers:
        container = docker_client.containers.get(container_name)
        if container.attrs["State"]["Status"] == "running":
            container.stop()

    if did_soak_test_fail_during:
        logger.error(
            "Failing because of alarms triggered during Soak Test. Dumping `docker-proxy` output: %s",
            os.popen(
                "tail -f /proc/%s/fd/1", soak_tests_docker_compose_process.pid()
            ).read(),
        )
        sys.exit(2)

    logger.info("Done polling Soak Test alarms.")
