# Use the correct base image for Ubuntu
FROM ubuntu:18.04

ENTRYPOINT []

# Update and install Python3, pip, and Rasa
RUN apt-get update && apt-get install -y python3 python3-pip && python3 -m pip install --no-cache --upgrade pip && pip3 install --no-cache rasa==3.6.20 --use-feature=2020-resolver

# Create a directory for the app
RUN mkdir /app

# Copy app directory to the container
ADD . /app/

# Set executable permission for your script
RUN chmod +x /app/start_services.sh

# Default command to start your services
CMD ["/app/start_services.sh"]
