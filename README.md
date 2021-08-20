# AWS OTel Python Soaking Tests Demo

This is a demo of running Soak Tests is an way that is easy to configure for other languages. The goals of this design are:
* Provide visibility even to anonymous users about the Soak Test results
* Detect anomalies in Soak Test results and appropriately alert when they occur

## Visibility of results

First, a graph of the actual Soak Tests is automatically published after every run. They are found at the [soak-tests/snapshosts folder on the gh-pages branch](https://github.com/NathanielRN/aws-otel-python-soaking-tests-demo/tree/gh-pages/soak-tests/snapshots). We use a separate `gh-pages` branch to separate the noise-y commits.

Second, a [graph visualization that shows how the overall averages of the Soak Tests changes between commits](https://nathanielrn.github.io/aws-otel-python-soaking-tests-demo/soak-tests/per-commit-overall-results/index.html) is automatically generated and hosted by GitHub pages.

## Useful Links

Find out more about AWS X-Ray Tracing with Opentelemetry Python at the
following links.

- [OpenTelemetry Python Core GitHub](https://github.com/open-telemetry/opentelemetry-python)
- [OpenTelemetry Python Contrib GitHub](https://github.com/open-telemetry/opentelemetry-python-contrib)
- [AWS OpenTelemetry Python SDK Extension Package](https://github.com/open-telemetry/opentelemetry-python-contrib/tree/master/sdk-extension/opentelemetry-sdk-extension-aws)
- [AWS Distro for OpenTelemetry](https://aws-otel.github.io/)

## License

This project is licensed under the Apache-2.0 License.
