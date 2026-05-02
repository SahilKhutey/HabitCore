FROM flink:1.17

# Install Python 3 and pip
USER root
RUN apt-get update && \
    apt-get install -y python3 python3-pip python3-dev && \
    rm -rf /var/lib/apt/lists/*

# Install PyFlink and dependencies
RUN pip3 install apache-flink kafka-python

USER flink
