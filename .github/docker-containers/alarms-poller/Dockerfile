FROM python:3.9

COPY . .

RUN pip install docker awscli

CMD python ./poll-during-soak-tests.py --polling-interval $HOSTMETRICS_COLLECTION_INTERVAL_IN_SECONDS;
