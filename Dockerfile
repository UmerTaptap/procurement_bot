FROM ubuntu:18.04
ENTRYPOINT []


# Install dependencies for Conda
RUN apt-get update && \
    apt-get install -y wget bzip2 && \
    apt-get clean

# Install Miniconda
RUN wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh && \
    bash Miniconda3-latest-Linux-x86_64.sh -b -p /opt/conda && \
    rm Miniconda3-latest-Linux-x86_64.sh && \
    /opt/conda/bin/conda clean -tipsy

# Update PATH
ENV PATH="/opt/conda/bin:${PATH}"

# Create a Conda environment with Python 3.9
RUN conda create -n myenv python=3.9 && \
    conda clean -a

# Activate the environment and install Rasa
RUN echo "source activate myenv" > ~/.bashrc
SHELL ["/bin/bash", "--login", "-c"]
RUN source activate myenv && \
    pip install --no-cache rasa

    
ADD . /app/
RUN chmod +x /app/start_services.sh
CMD /app/start_services.sh