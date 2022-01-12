FROM ubuntu:latest

RUN apt-get update
RUN apt-get install software-properties-common -y
RUN apt-get install build-essential -y
RUN apt-get install net-tools -y
RUN apt-get install python3-pip -y
RUN apt-get install python3-dev -y

RUN apt-get install libssl-dev -y
RUN apt-get install libffi-dev -y
RUN apt-get install cargo -y

RUN python3 -m pip install -U pip

RUN python3 -m pip install redis -U
RUN python3 -m pip install sanic -U

RUN python3 -m pip install python-pptx -U
RUN python3 -m pip install sanic-jwt-extended --pre -U
RUN python3 -m pip install natsort -U
RUN python3 -m pip install pytz -U
RUN python3 -m pip install dateutil -U
RUN python3 -m pip install magic -U
RUN python3 -m pip install ulid -U
RUN python3 -m pip install jwt -U
RUN python3 -m pip install cryptography -U

COPY . /home
WORKDIR "/home/"


# ENTRYPOINT [ "/bin/bash" ]
# sudo docker run --rm -it --entrypoint bash public-ppt-interactive-generator-server:latest
# -v $(pwd)/config.py:/root/app/config.py
# --mount type=bind,source=/tmp/a.txt,target=/root/a.txt
ENTRYPOINT [ "python3" , "/home/server.py" ]