ARG TAG="latest"
FROM ubuntu:22.04

ENV container docker
ENV LC_ALL C
ENV DEBIAN_FRONTEND noninteractive

# match the stop signal to systemd's.
STOPSIGNAL SIGRTMIN+3

USER root
WORKDIR /root

RUN apt-get update -y \
    && apt-get install --no-install-recommends -y systemd \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/* \
    # allow login
    && rm -f /var/run/nologin

# remove all unnecessary service.
RUN rm -f \
    /etc/systemd/system/*.wants/* \
    /lib/systemd/system/*.wants/*

# optional: enable journald.
# known issus: audit won't work under rootless env due to permission.
RUN cd /lib/systemd/system \
    && ln -s ../systemd-journald.socket ./sockets.target.wants/systemd-journald.socket \
    && ln -s ../systemd-journald-audit.socket ./sockets.target.wants/systemd-journald-audit.socket \
    && ln -s ../systemd-journald-dev-log.socket ./sockets.target.wants/systemd-journald-dev-log.socket \
    && ln -s ../systemd-journald.service ./sysinit.target.wants/systemd-journald.service \
    && ln -s ../systemd-journal-flush.service ./sysinit.target.wants/systemd-journal-flush.service

# VOLUME [ "/tmp", "/run", "/run/lock" ]

# install python3.10 and openai emvironment
COPY ./notebook /opt/notebook
RUN <<EOF
    apt-get update -y
    apt-get install -y python3.10 python3.10-venv
    (cd /opt/notebook; /usr/bin/python3.10 -m venv .venv)
    . /opt/notebook/.venv/bin/activate
    pip install -r /opt/notebook/requirements.txt 
    deactivate
    apt-get clean
    rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*
EOF

# Install Development Environment
RUN <<EOF
    apt-get update -y
    apt-get install -y git curl wget ssh
    apt-get clean
    rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*
EOF

CMD [ "/lib/systemd/systemd" ]

