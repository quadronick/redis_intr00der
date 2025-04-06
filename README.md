# Redis Intruder 

Redis Intruder is a simple HTTP server that fetches and displays Redis INFO metrics in a web browser. 
It connects to a remote Redis instance, retrieves its information using the INFO ALL command, processes the data for better readability, and serves it via an HTTP interface. 
It's Redis metrics exporter, basically.

This tool is useful for monitoring and debugging Redis instances by exposing key metrics to Prometheus or Victoria Metrics. 
     

# Features 

    Redis Metrics Retrieval : Fetches all available Redis metrics using the INFO ALL command.
    Metrics Renaming : Processes and renames certain Redis metric keys for better clarity and consistency.
    HTTP Interface : Exposes the processed Redis metrics through a simple HTML page.
    Authentication Support : Supports password-protected Redis instances.
    Error Handling : Provides basic error messages when the connection fails or other issues arise.
     

# Prerequisites 

    Python 3.x
    A running Redis instance (with or without authentication)
    Basic knowledge of environment variables and networking
     

# Installation 

    Clone or download this repository.
    Ensure you have Python 3 installed on your system.
    You may use Docker image as well 
     

# Usage (considering you are in project root directory)

### Step 1: Set Environment Variables 

Before running the script, configure the following environment variables: 
```
REDIS_INTR00DER_TARGET_HOST => The hostname or IP address of the Redis server => 127.0.0.1
REDIS_INTR00DER_TARGET_HOST_PORT => The port number of the Redis server => 6379
REDIS_INTR00DER_TARGET_HOST_PASSWORD => The password for the Redis server (optional) => mypassword
```

You can set these variables in your terminal as follows: 
 
```
export REDIS_INTR00DER_TARGET_HOST="127.0.0.1"
export REDIS_INTR00DER_TARGET_HOST_PORT="6379"
export REDIS_INTR00DER_TARGET_HOST_PASSWORD="mypassword"  # Leave empty if no password
``` 

### Step 2: Run the Server 

Execute the script: 
`python redis_intr00der/__init__.py`

The server will start and display the following message: 
`Exporting at ://0.0.0.0:6339/`
 
### Step 3: Access the Web Interface 

Open your web browser and navigate to: 
`http://<your-server-ip>:6339/`
 
Replace <your-server-ip> with the actual IP address or hostname where the server is running. For example: 
`http://127.0.0.1:6339/`

## Docker usage variant: 

### Step 1: Build docker image

Execute: 
`docker buildx build . -t redis_intr00der:latest`

### Step 2: Run the Server

Execute: 
```
docker run --rm
    --name redis_intr00der \
    -p 6339:6339 \
    -e REDIS_INTR00DER_TARGET_HOST="127.0.0.1" \
    -e REDIS_INTR00DER_TARGET_HOST_PORT="6379" \
    -e REDIS_INTR00DER_TARGET_HOST_PASSWORD="secured-pass-here" \
    redis_intr00der:latest
```

### Step 3: 
Open your web browser and navigate to: 
`http://<your-server-ip>:6339/`
 
Replace <your-server-ip> with the actual IP address or hostname where the server is running. For example: 
`http://127.0.0.1:6339/`

# License 

This project is licensed under the MIT License. See the LICENSE  file for details. 
