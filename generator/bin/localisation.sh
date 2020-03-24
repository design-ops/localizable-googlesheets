#!/bin/bash

source "$( dirname "${BASH_SOURCE[0]}" )/utils.sh"

script_dir="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
plugin_project_path="$script_dir/.."
output_dir="$script_dir/../output/"
sheet_name="Translations"
plurals_sheet_name="Plurals"
development=false

function show_help_and_exit {
    cat <<HELPTEXT

run - generate localisations from GoogleSheets.
Generates and copies a CSV with all the localisations, all the required enums, and the localisable.strings files.
Ensure that you are running this in the root of the repo.

SYNOPSIS

    ./bin/localisation.sh

MANDATORY ARGUMENTS

    -s <id> id of google sheet to process
    -p <path> path to the project dir to automatically update files
    -c <path> path to the google cloud credentials

OPTIONAL ARGUMENTS

    -b  specify this flag to bypass the csv generation and use the csv file that's in the specified Xcode project folder
    -o <path> path to folder to generate code into (defaults to output folder in project)
    -h  display this help text
    -d  run in development mode

HELPTEXT
    exit 1
}

function check_docker_image_installed {
    if docker images | tr -s " " | grep 'localizable-googlesheets 1.1' &> /dev/null ; then
        echo "👍 Docker image is installed"
    else
        cat <<NO_CODEGEN_IMAGE
🚨🚨🚨🚨🚨🚨🚨🚨🚨🚨

ERROR - the Docker image does not appear to be installed

Run the setup.sh to build the docker image and try again.

NO_CODEGEN_IMAGE
        exit 1
    fi
}

# Docker on OS X requires an additional arg so we need to know if we are on a mac.
function check_for_osx {
    if uname | grep 'Darwin' &> /dev/null ; then
        echo "🍎 running on a mac"
        running_on_osx=true
        expose_computer_to_docker="-v /Users:/Users"
    else
        echo "🤓 not running on a mac"
        # presume we're running on Linux
        expose_computer_to_docker="-v /home:/home"
    fi

}

# Creates the output directory for the code generator and returns the fully qualified path.
# Note - we echo out the result of the function so we can capture this in a result variable.
function generate_output_directory {
    local full_output_folder_path=$1

    # local dir_name=$(date "+generated_%Y%m%d_%H%M-%S")

    if [ "$development" = true ] ; then
      local dir_name=$(date "+generated_%Y%m%d_%H%M-%S")
    else
      local dir_name="generated"
    fi

    local full_output_path="$full_output_folder_path$dir_name"

    echo -n $full_output_path
}


function run_docker_localisation {
    if [ -z "${sheet_id}" ] || [ -z ${project_dir} ]
    then
        show_help_and_exit
    fi

    echo "👍 running build with sheet id '${sheet_id}' and name '${sheet_name}', plurals name '${plurals_sheet_name}' development ${development}"
    output_dir=$(generate_output_directory ${output_dir})

    local final_project_dir
    case ${project_dir} in
        /*) final_project_dir=${project_dir} ;;
        *) final_project_dir="$plugin_project_path/$project_dir" ;;
    esac

    python_command="python -u localisation/process_localisation_cli.py
                            --sheet-id ${sheet_id}
                            --sheet-name ${sheet_name}
                            --plurals-sheet-name ${plurals_sheet_name}
                            --credentials ${credentials}
                            --output ${output_dir}
                            --project-dir ${final_project_dir}"

    if [ "${skip_csv}" = true ]; then
        python_command="$python_command --skip-csv"
    fi

    docker_command="docker run -v ${plugin_project_path}:/work ${expose_computer_to_docker} -w /work -i -e PYTHONUNBUFFERED=0 localizable-googlesheets ${python_command}"

    ${docker_command}
}

# Parse command line args...
while getopts s:n:p:c:m:o:hb opt; do
    case $opt in
        s)
            sheet_id=$OPTARG
            ;;
        n)
            sheet_name=$OPTARG
            ;;
        p)
            project_dir=$OPTARG
            ;;
        c)
            credentials=$OPTARG
            ;;
        o)
            output_dir=$OPTARG
            ;;
        b)
            skip_csv=true
            ;;
        d)
            development=true
            ;;
        h | *)
            show_help_and_exit
            ;;
        :)
            echo "Missing option argument for -$OPTARG" >&2
            ;;
        \?)
            echo "Invalid option: -$OPTARG"
            show_help_and_exit
            ;;
    esac
done

check_docker_is_installed
check_docker_image_installed
check_for_osx
run_docker_localisation
