FROM ubuntu:18.04
ENTRYPOINT []



# Install Python 3.9 and pip
RUN apt-get update && \
    apt-get install -y software-properties-common && \
    add-apt-repository ppa:deadsnakes/ppa && \
    apt-get update && \
    apt-get install -y python3.9 python3.9-distutils python3.9-venv curl && \
    curl -sS https://bootstrap.pypa.io/get-pip.py | python3.9

# Upgrade pip and install Rasa
RUN python3.9 -m pip install --no-cache --upgrade pip && \
    python3.9 -m pip install --no-cache rasa



ADD . /app/
RUN chmod +x /app/start_services.sh
CMD /app/start_services.sh