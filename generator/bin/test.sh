#!/usr/bin/env bash

source "$( dirname "${BASH_SOURCE[0]}" )/utils.sh"

check_docker_is_installed

docker run localizable-googlesheets python -m unittest