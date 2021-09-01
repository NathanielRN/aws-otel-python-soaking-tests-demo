import time
import sys
import argparse
from threading import Timer
import psutil
from psutil import NoSuchProcess
from io import StringIO
from contextlib import redirect_stdout
import json

import logging

logging.basicConfig(level=logging.INFO)

logger = logging.getLogger(__file__)


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
    args = parse_args()

    class Watchdog(Exception):
        def __init__(self, timeout, userHandler=None):
            self.timeout = timeout
            self.handler = (
                userHandler if userHandler is not None else self.defaultHandler
            )
            self.timer = Timer(self.timeout, self.handler)

        def reset(self):
            self.timer.cancel()
            self.timer = Timer(self.timeout, self.handler)
            self.timer.start()

        def start(self):
            self.timer.start()

        def cancel(self):
            self.timer.cancel()

        def defaultHandler(self):
            raise self

    watchdog = Watchdog(10)
    watchdog.start()

    soak_tests_docker_compose_process: psutil.Process = None

    try:
        while not soak_tests_docker_compose_process:
            try:
                for process in psutil.process_iter():
                    if process.name() == "docker-compose":
                        soak_tests_docker_compose_process = process
                        break
            except NoSuchProcess as exc:
                pass
            time.sleep(1)
    except Watchdog as exc:
        logger.error(
            "Soak Tests `docker-compose` process did not start after %s seconds",
            watchdog.timeout,
        )
        sys.exit(1)

    watchdog.cancel()

    did_soak_test_fail_during = False

    while psutil.pid_exists(soak_tests_docker_compose_process.pid()):
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
            "Failing because of alarms triggered during Soak Test. Dumping docker-compose output: %s",
            exec(
                "tail -f /proc/%s/fd/1", soak_tests_docker_compose_process.pid()
            ),
        )
        sys.exit(1)

    logger.info("Done polling Soak Test alarms.")
