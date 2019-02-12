# Base image
FROM python:2.7-stretch

# Package manager
RUN apt-get update && apt-get install telnet

# Install Python modules
# Install newest version of pyvomi from pypi
RUN pip install pyvmomi==6.0.0
RUN pip install pyVim

# Copy code from repository to image
COPY ./vmware-api-inventory /usr/src

# Start in default source directory
WORKDIR /usr/src/
