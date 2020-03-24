#!/usr/bin/env bash

function check_docker_is_installed {
    if hash docker &> /dev/null ; then
        echo "docker is installed"
    else
        cat <<NO_DOCKER

ERROR - docker does not appear to be installed

Please ensure docker is installed and that the docker command is available on the command line.

Get docker here - https://www.docker.com/get-docker

Once installed check that you can run it from the command line by running

    docker -v

which should return the installed docker version.

NO_DOCKER
        exit 1
    fi
}
