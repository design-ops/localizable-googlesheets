#!/bin/bash

# Build the Docker image for the current project

source "$( dirname "${BASH_SOURCE[0]}" )/utils.sh"

script_dir="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
plugin_project_path="$script_dir/.."

check_docker_is_installed

echo "Building the Docker image..."
cd ${plugin_project_path}
docker build -t localizable-googlesheets:1.1 -t localizable-googlesheets:latest .
echo "Finished."

