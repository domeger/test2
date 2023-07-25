FROM python:3.9-slim as bkstart

### BEEKEEPER START LOGIC BEGINS HERE ###
RUN apt update && apt install build-essential -y
COPY requirements.txt requirements.txt
RUN pip3 install --no-cache-dir -r requirements.txt

### YOUR DOCKERFILE STEPS BEGIN BELOW
FROM bkstart as modelownerstart

# This is an example application that runs app.py to provide an inference interface to a
# COVID detection model
# Use working directory /app
WORKDIR /app

# Copy the content of current directory to /app
COPY app.py /app/app.py
COPY models /app/models

EXPOSE 5000
### YOUR DOCKERFILE STEPS END HERE ###

############################################################################################

ENTRYPOINT ["python3", "app.py"]
