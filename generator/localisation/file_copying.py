from os import path, walk
from shutil import copy, SameFileError

from localisation import CHECKSUM_FILENAME


CHECKSUM_VALIDATOR_SCRIPT_LOCATION = "./templates"
CHECKSUM_VALIDATOR_SCRIPT_NAME = "validate_checksum.sh"


def copy_xcode_files( csv_paths: [str],
                      enum_path: str,
                      stringsdict_path: dict,
                      strings_path: dict,
                      checksum_path: str,
                      project_dir: str) -> bool:
    """
    Copies the files generated from the localisation process to the required project directory.
    To do the copying, it runs through the target project directory and finds a file with the same name
    as the file it wants to copy, then copies it.
    Returns `True` if successfully copied, `False` otherwise.
    """
    if not path.isdir(project_dir):
        print("WARNING: Couldn't find Xcode Project dir {}, generated files won't be copied!".format(project_dir))
        return False

    enum_name = path.basename(enum_path)
    enum_copied = False

    checksum_copied = False

    # {"en": "/Users/.....", "ja": "/Users/...."}
    stringsdict_copied = [False] * len(stringsdict_path.keys())
    strings_copied = [False] * len(strings_path.keys())

    for dirpath, _, files in walk(project_dir):
        if "DerivedData" in dirpath or ".app" in dirpath:
            continue

        csv_paths_copy = list(csv_paths)
        for csv_path in csv_paths_copy:
            csv_name = path.basename(csv_path)
            if not len(csv_paths) == 0 and csv_name in files:
                copy(csv_path, dirpath)
                csv_paths.remove(csv_path)
                print("Updated {} at {}".format(csv_name, dirpath))

        try:
            if not checksum_copied and CHECKSUM_FILENAME in files:
                copy(checksum_path, dirpath)
                copy(path.join(CHECKSUM_VALIDATOR_SCRIPT_LOCATION, CHECKSUM_VALIDATOR_SCRIPT_NAME),
                     path.join(dirpath, CHECKSUM_VALIDATOR_SCRIPT_NAME))
                checksum_copied = True
                print("Updated {} at {}".format(CHECKSUM_FILENAME, dirpath))
        except SameFileError:
            checksum_copied = True
            continue

        if not enum_copied and enum_name.upper() in (file.upper() for file in files):
            copy(enum_path, dirpath)
            enum_copied = True
            print("Updated {} at {}".format(enum_name, dirpath))

        if ".lproj" in dirpath and ".bundle" not in dirpath:
            if "Localizable.strings" in files:
                for localisation in strings_path.keys():
                    if localisation in path.basename(dirpath):
                        copy(strings_path[localisation], path.join(dirpath, "Localizable.strings"))
                        strings_copied.pop()
                        print("Updated {} at {}".format(path.basename(strings_path[localisation]), dirpath))
            if "Localizable.stringsdict" in files:
                for localisation in stringsdict_path.keys():
                    if localisation in path.basename(dirpath):
                        copy(stringsdict_path[localisation], path.join(dirpath, "Localizable.stringsdict"))
                        stringsdict_copied.pop()
                        print("Updated {} at {}".format(path.basename(stringsdict_path[localisation]), dirpath))

    if not len(csv_paths) == 0 or not enum_copied or stringsdict_path or not checksum_copied:
        if not len(csv_paths) == 0:
            for csv_path in csv_paths:
                copy(csv_path, project_dir)
                print("Added {} into {}".format(csv_name, project_dir))
        if not checksum_copied:
            copy(checksum_path, project_dir)
            copy(path.join(CHECKSUM_VALIDATOR_SCRIPT_LOCATION, CHECKSUM_VALIDATOR_SCRIPT_NAME),
                 path.join(dirpath, CHECKSUM_VALIDATOR_SCRIPT_NAME))
            print("Added {} into {}".format(CHECKSUM_FILENAME, project_dir))
        if not enum_copied:
            print("\n\nWARNING: Couldn't find enum file to replace. Please add \n  {}\nto your Xcode project.\n\n"
                  .format(enum_path))
        if stringsdict_copied:
            print("WARNING: Couldn't copy STRINGSDICT files, couldn't find an existing one!")
        return False

    return True
