FROM 312989076726.dkr.ecr.us-east-2.amazonaws.com/itx_python3.10_lambda

ARG LAMBDA_TASK_ROOT="/approot"
ARG LAMBDA_NAME=""
ARG LAMBDA_VERSION=""

WORKDIR /tmp
COPY requirements.txt .

RUN set -eux; \
    mkdir -p /var/lib/dpkg; \
    touch /var/lib/dpkg/status; \
    apt-get update; \
    apt-get -y dist-upgrade; \
    apt-get clean all; \
    rm -rf /var/lib/apt/lists/*; \
    pip3 install -r requirements.txt; \
    rm -Rf requirements.txt

WORKDIR ${LAMBDA_TASK_ROOT}
COPY src ${LAMBDA_TASK_ROOT}


ENTRYPOINT ["/entry_script.sh"]
CMD [ "app.lambda_handler" ]
