import subprocess
import sys

subprocess.check_call([sys.executable, "-m", "pip", "install", "boto3"])

import argparse
import logging
from statistics import mean
from datetime import datetime, timedelta

import boto3

logging.basicConfig(level=logging.INFO)

logger = logging.getLogger(__file__)

# AWS Client API Constants

PROCESS_COMMAND_LINE_DIMENSION_NAME = "process.command_line"
METRIC_DATA_STATISTIC = "Sum"


def parse_args():
    parser = argparse.ArgumentParser(
        description="""
        produce-performance-test-results.py produces overall results for the
        performance tests that were just run as JSON output.
        """
    )

    parser.add_argument(
        "--metrics-period",
        required=True,
        type=int,
        help="""
        The interval at which performance metrics are collected. This is the
        period used for the metrics monitored by the alarms and is the interval
        with which the script polls the Performance Test alarms (in seconds).

        Examples:

            --metrics-period=600
        """,
    )

    parser.add_argument(
        "--num-of-cpus",
        required=True,
        type=int,
        help="""
        The number of CPUs used when running the performance tests.

        Examples:

            --num-of-cpus=2
        """,
    )

    parser.add_argument(
        "--logs-namespace",
        required=True,
        help="""
        The namespace of the logs that the alarm should poll.

        Examples:

            --logs-namespace=aws-observability/aws-otel-python/soak-tests
        """,
    )

    parser.add_argument(
        "--process-command-line-dimension-value",
        required=True,
        help="""
        The Cloudwatch metric dimension value which corresponds to the command
        line string used to run the sample app process. This sample app is the
        one being tested for performance. The alarms being polled in this script
        monitor metrics which contain this dimension value.

        Examples:

            --process-command-line-dimension-value='/usr/local/bin/python3 application.py'
        """,
    )

    return parser.parse_args()


if __name__ == "__main__":
    logger.debug("Starting script to get performance test results.")

    start_time = (datetime.utcnow() - timedelta(hours=1)).strftime("%FT%TZ")

    args = parse_args()

    cpu_load_metric_data_queries = [
        {
            "Id": "cpu_time_raw",
            "MetricStat": {
                "Metric": {
                    "Namespace": args.logs_namespace,
                    "MetricName": "process.cpu.time",
                    "Dimensions": [
                        {
                            "Name": PROCESS_COMMAND_LINE_DIMENSION_NAME,
                            "Value": args.process_command_line_dimension_value,
                        }
                    ],
                },
                "Stat": METRIC_DATA_STATISTIC,
                "Period": args.metrics_period,
            },
            "Label": "CPU Time Raw",
            "ReturnData": False,
        },
        {
            "Id": "cpu_load_expr",
            "Expression": f"cpu_time_raw/PERIOD(cpu_time_raw)/{args.num_of_cpus}*100",
            "Label": f"CPU Load Percentage for {args.num_of_cpus} CPUs",
            "ReturnData": True,
            "Period": args.metrics_period,
        },
    ]

    total_memory_metric_data_queries = [
        {
            "Id": "virtual_memory_raw",
            "MetricStat": {
                "Metric": {
                    "Namespace": args.logs_namespace,
                    "MetricName": "process.memory.virtual_usage",
                    "Dimensions": [
                        {
                            "Name": PROCESS_COMMAND_LINE_DIMENSION_NAME,
                            "Value": args.process_command_line_dimension_value,
                        }
                    ],
                },
                "Stat": METRIC_DATA_STATISTIC,
                "Period": args.metrics_period,
            },
            "Label": "Virtual Memory",
            "ReturnData": False,
        },
        {
            "Id": "physical_memory_raw",
            "MetricStat": {
                "Metric": {
                    "Namespace": args.logs_namespace,
                    "MetricName": "process.memory.physical_usage",
                    "Dimensions": [
                        {
                            "Name": "process.command_line",
                            "Value": args.process_command_line_dimensions_value,
                        }
                    ],
                },
                "Stat": METRIC_DATA_STATISTIC,
                "Period": args.metrics_period,
            },
            "Label": "Physical Memory",
            "ReturnData": False,
        },
        {
            "Id": "total_memory_expr",
            "Expression": "SUM([virtual_memory_raw])",
            "Label": "Total Memory",
            "ReturnData": True,
            "Period": args.metrics_period,
        },
    ]

    aws_client = boto3.client("cloudwatch")

    metric_data_results = aws_client.get_metric_data(
        StartTime=start_time,
        EndTime=datetime.utcnow(),
        MetricDataQueries=cpu_load_metric_data_queries
        + total_memory_metric_data_queries,
    )["MetricDataResults"]

    benchmarks_json = {
        "benchmarks": [
            {
                "Name": "Soak Test Average CPU Load",
                "Value": mean(
                    next(
                        metric_data
                        for metric_data in metric_data_results
                        if metric_data["Id"] == "cpu_load_expr"
                    )["Values"]
                )
                / args.metrics_period
                / args.num_of_cpus
                * 100,
                "Unit": "Percent",
            },
            {
                "Name": "Soak Test Average Virtual Memory Used",
                "Value": mean(
                    next(
                        metric_data
                        for metric_data in metric_data_results
                        if metric_data["Id"] == "total_memory_expr"
                    )["Values"]
                )
                / (2 ** 20),
                "Unit": "Megabytes",
            },
        ]
    }

    logger.info("Found these benchmarks: ", benchmarks_json)

    with open("output.json", "w") as file_context:
        file_context.write(benchmarks_json)

    logger.info("Done polling Performance Test alarms.")
