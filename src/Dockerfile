FROM ubuntu

RUN apt-get update
RUN apt-get update \
    && DEBIAN_FRONTEND=noninteractive apt-get install -y \
                                                 python3 \
                                        && apt-get clean \
                            && rm -rf /var/lib/apt/lists/*

RUN apt-get update \
    && DEBIAN_FRONTEND=noninteractive apt-get install -y \
                                                  netcat \
                                        && apt-get clean \
                            && rm -rf /var/lib/apt/lists/*

RUN apt-get update \
&& DEBIAN_FRONTEND=noninteractive apt-get install -y \
                                         python3-pip \
                                    && apt-get clean \
                        && rm -rf /var/lib/apt/lists/*

RUN apt-get update \
&& DEBIAN_FRONTEND=noninteractive apt-get install -y \
                                            gunicorn \
                                    && apt-get clean \
                        && rm -rf /var/lib/apt/lists/*


RUN groupadd -g 999 flaskuser && \
    useradd -r --create-home -u 999 -g flaskuser flaskuser
USER flaskuser
WORKDIR /home/flaskuser
ENV PATH="/home/flaskuser/.local/bin:${PATH}"

COPY --chown=flaskuser requirements.txt /home/flaskuser/requirements.txt
RUN pip3 install --user --no-cache-dir --trusted-host pypi.python.org -r /home/flaskuser/requirements.txt
COPY --chown=flaskuser . /home/flaskuser
ADD --chown=flaskuser . /home/flaskuser/app

RUN chmod +x /home/flaskuser/entrypoint.sh
ENTRYPOINT ["/home/flaskuser/entrypoint.sh"]
