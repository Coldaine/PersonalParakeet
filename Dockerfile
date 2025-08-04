FROM ubuntu:22.04

# Install system dependencies
RUN apt-get update && apt-get install -y     build-essential     curl     git     libasound2-dev     libportaudio2     libportaudiocpp0     portaudio19-dev     python3-dev     python3-pip     python3-venv

# Install Conda
RUN curl -o miniconda.sh https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh &&     bash ./miniconda.sh -b -p /opt/conda &&     rm miniconda.sh

# Set up Conda environment
ENV PATH /opt/conda/bin:$PATH
COPY environment.yml /app/environment.yml
RUN conda env create -f /app/environment.yml

# Copy the application code
COPY . /app
WORKDIR /app

# Install Python dependencies
RUN . /opt/conda/etc/profile.d/conda.sh &&     conda activate personalparakeet &&     poetry install &&     pip install -r requirements-torch.txt &&     pip install -r requirements-ml.txt

# Run the application
CMD ["/opt/conda/envs/personalparakeet/bin/python", "-m", "personalparakeet"]