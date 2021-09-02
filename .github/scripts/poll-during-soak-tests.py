import argparse
import json
import logging
import sys
import time
from contextlib import redirect_stdout
from io import StringIO

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
                if "docker" in process.name():
                    print("DEBUG: Found this process name - %s", process.name())
                if process.name() == "dockerd":
                    soak_tests_docker_compose_process = process
                    logger.info("Found matching process: %s", str(process))
                    break
        except NoSuchProcess as exc:
            pass
        if time.time() - start > SOAK_TESTS_STARTED_TIMEOUT:
            logger.error(
                "Soak Tests `dockerd` process did not start after %s seconds",
                SOAK_TESTS_STARTED_TIMEOUT,
            )
            exec("exit 1")

    did_soak_test_fail_during = False

    while psutil.pid_exists(soak_tests_docker_compose_process.pid):
        shell_output_buffer = StringIO()

        with redirect_stdout(shell_output_buffer):
            exec(
                "aws cloudwatch describe-alarms --alarm-name-prefix 'OTel Python Soak Tests - '"
            )

        alarms_info = json.loads(shell_output_buffer.getvalue())

        for alarm in alarms_info["MetricAlarms"]:
            if alarm["StateValue"] == "ALARM":
                logger.error(
                    "Triggered alarm %s with reason: %s",
                    alarm["AlarmName"],
                    alarm["StateReason"],
                )
                did_soak_test_fail_during = True

        time.sleep(args.polling_interval)

    if did_soak_test_fail_during:
        logger.error(
            "Failing because of alarms triggered during Soak Test. Dumping dockerd output: %s",
            exec(
                "tail -f /proc/%s/fd/1", soak_tests_docker_compose_process.pid()
            ),
        )
        exec("exit 1")

    logger.info("Done polling Soak Test alarms.")
