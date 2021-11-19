FROM ubuntu:latest

RUN apt-get update
RUN apt-get install software-properties-common -y
RUN apt-get install build-essential -y
RUN apt-get install net-tools -y
RUN apt-get install python3-pip -y
RUN apt-get install python3-dev -y
RUN apt-get install dbus -y

RUN python3 -m pip install -U pip

RUN python3 -m pip install redis
RUN python3 -m pip install sanic
# RUN python3 -m pip install dbus

VOLUME [ "/sys/fs/cgroup" , "/sys/fs/cgroup" ]
#VOLUME [ "/run/user/1000/bus" , "/run/user/1000/bus" ]

ENV XDG_RUNTIME_DIR "/run/user/1000"
ENV DBUS_SESSION_BUS_ADDRESS "unix:path=/run/user/1000/bus"

COPY python_app /home/python_app
WORKDIR "/home/python_app"

#ENTRYPOINT [ "python3" , "server.py" ]

ENTRYPOINT [ "/bin/bash" ]
