FROM ubuntu:18.04
ENTRYPOINT []

# Update package lists and install prerequisites
RUN apt-get update && apt-get install -y software-properties-common

# Add deadsnakes PPA for Python 3.9
RUN add-apt-repository ppa:deadsnakes/ppa

# Update package lists again
RUN apt-get update

# Install Python 3.9 and pip
RUN apt-get install -y python3.9 python3.9-pip

# Upgrade pip
RUN python3.9 -m pip install --no-cache --upgrade pip

# Install rasa using pip3 (optional, for clarity)
RUN pip3 install --no-cache rasa
ADD . /app/
RUN chmod +x /app/start_services.sh
CMD /app/start_services.sh