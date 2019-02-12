# vmware-cli
A simple vmware-cli for the purpose of gathering asset inventory and parsing into python dictionaries to be imported into other systems.

## Local Development Environment
Step 1: Copy config file
Based on the config-sample.py create a file config.py with the hostname, credentials and port number
Do not commit the config file to the repository

Step 2: Build docker image
docker build --no-cache -t vmware-local-dev .

Step 3: Run Docker image

Run Docker image, mount in local directory into the container as a volume and start a shell
docker run --rm -it -v "$(pwd)/vmware-api-inventory":/usr/src vmware-local-dev bash
