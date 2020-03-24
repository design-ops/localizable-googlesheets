import sys
from time import time

import os
from enum import Enum, auto
from string import ascii_uppercase
from typing import Dict, List, Optional, Tuple, TypeVar, NewType
from tempfile import gettempdir

from localisation.utils import create_checksum
from localisation.validator import validate, validate_plurals
from localisation.file_copying import copy_xcode_files
from localisation.output.enum_builder import output_enums
from localisation.output.stringsfile_builder import output_localisable_strings
from localisation.googlesheethelper import GoogleSheetHelper
from localisation.output.template_helper import TemplateGenerator
from localisation.output.csv_builder import build_csv, build_localisations
from localisation import CHECKSUM_FILENAME, PLURAL_KEYS_VALUE
from localisation.parser.sheet_parser import parse

KEYS_ROW = 1
PLURALS_VALUE = "plurals"
KEYS_VALUE = "key"
PLURALS_START_ROW = 1


class FilepathKey(Enum):
    csv = auto()
    enums = auto()
    stringsdict = auto()
    strings = auto()
    checksum = auto()


class Localisation:

    def __init__(self,
                 google_sheet_helper: GoogleSheetHelper,
                 template_generator: TemplateGenerator,
                 output_dir: Optional[str],
                 project_dir: str):
        self.__google_sheet_helper = google_sheet_helper
        self.__template_generator = template_generator
        self.__output_dir = output_dir if output_dir else "../output/{}".format(int(time()))
        self.__project_dir = project_dir if os.path.isabs(project_dir) \
            else os.path.join(os.path.dirname(os.path.abspath(__file__)), project_dir)
        print("Xcode project path is {}".format(self.__project_dir))

        self.__project_name = None
        for root, dirs, files in os.walk(self.__project_dir):
            for dir in (dir for dir in dirs if dir.lower().endswith("xcworkspace")):
                self.__project_name = dir.split(".")[0]
                break
            if self.__project_name:
                break

    def __get_keys_row(self) -> Dict:
        """
        Returns a dict built from the row with the keys and locales.
        Dict format: {'key': 'column letter (i.e. A, B, C...)', 'locale1': 'column letter (i.e. A, B, C...)', 'locale2: 'column letter (i.e. A, B, C...)', ...}

        Throws KeyError and IndexError
        """
        dict = {}
        key_values = self.__google_sheet_helper.get_values(start_at=KEYS_ROW)
        key_values_array = key_values[0]

        for value, column in zip(key_values_array, ascii_uppercase):
            value = value.partition("-")[0].strip()
            if not value:
                continue
            print("__get_keys_row {} at {}".format(value, column))
            dict[value] = column
        return dict

    def __get_plural_keys_row(self) -> Dict:
        """
        Builds an object like:
        {
            "variable": "A",
            "lang": "C",
            "zero": "D",
            "one": "E",
        }
        """
        dict = {}
        key_values = self.__google_sheet_helper.get_plurals_values(start_at=PLURALS_START_ROW)
        key_values_array = key_values[0]

        for value, column in zip(key_values_array, ascii_uppercase):
            if not value: continue
            if value == "EXAMPLE": continue

            dict[value] = column
        return dict

    def __build_localisation_dict(self, keys_dict: Dict) -> Dict:
        """
        Builds and returns a dict with all the keys and localizations
        The key is either the literal string 'key' or the locale.
        The value for each is an array of strings for each row.
        Throws KeyError and IndexError
        :return:
        {
            "key": ["some.key", "another.key"],
            "en": ["Some translation", "Another translation"],
            "es": ["Some translation in Spanish", "Another translation in Spanish"]
        }
        """

        localisation_values = {}
        for key in keys_dict.keys():
            localisation_values[key] = [array[0] if array else "" for array in
                                        self.__google_sheet_helper.get_values(start_at=keys_dict[key])[KEYS_ROW:]]

        return localisation_values

    def __build_plurals(self, plural_keys: Dict) -> Dict:
        plurals = {}
        for key in plural_keys.keys():
            plurals[key] = [array[0] if array else "" for array in
                            self.__google_sheet_helper.get_plurals_values(start_at=plural_keys[key])[
                            PLURALS_START_ROW:]]
        return plurals

    def localise(self, skip_csv_generation: bool) -> Optional[dict]:
        """
        Starts the process of creating the localised files.
        Builds a localisation dictionary
        """
        # If we're skipping past the CSV generation we don't have to:
        # Download the sheet
        # Build the CSV
        localisation_dict = {}
        plurals_dict = {}
        localisations_csv_name = "translations.csv"
        plurals_csv_name = "plurals.csv"
        if skip_csv_generation:
            csv_locations = [os.path.join(self.__project_dir, filename) for filename in
                             [localisations_csv_name, plurals_csv_name]]
            locs = build_localisations(csv_locations=csv_locations)
            localisation_dict = locs[0]
            plurals_dict = locs[1]
        else:
            keys = self.__get_keys_row()
            plural_keys = self.__get_plural_keys_row()
            try:
                keys_column = keys[KEYS_VALUE]
                plural_keys_column = plural_keys[PLURAL_KEYS_VALUE]
            except KeyError:
                print("The file needs a row with the app keys and a plurals sheet!")
                sys.exit(-1)

            localisation_dict = self.__build_localisation_dict(keys)
            plurals_dict = self.__build_plurals(plural_keys)
            # Save into a new set of CSV files
            files = build_csv(localisation_dict, plurals_dict, localisations_csv_name, plurals_csv_name,
                              output_dir=os.path.join(self.__output_dir, "csv"))

        # Validate
        validated_dicts = {}
        for localisation in filter(lambda x: (x != KEYS_VALUE), localisation_dict.keys()):
            print("Validating localisation for {}".format(localisation))
            validation_result = validate(localisation, localisation_dict[KEYS_VALUE],
                                         localisation_dict[localisation])
            validated_dicts[localisation] = validation_result.result
            for missing_key in validation_result.missing_keys:
                print("Missing key for value '{}'".format(missing_key))
            for missing_value in validation_result.missing_values:
                print("Missing {} value for key '{}'".format(missing_value.localisation, missing_value.key))

        # Validate plurals
        validated_plurals = validate_plurals(plurals_dict)

        # For each localisation, for each variable, combine them
        parsed_localisations = parse(validated_dicts, validated_plurals)

        localisables = output_localisable_strings(localisations=parsed_localisations,
                                                  template_generator=self.__template_generator,
                                                  output_dir=self.__output_dir,
                                                  project_name=self.__project_name)
        enum_paths = output_enums(localisations=parsed_localisations,
                                  template_generator=self.__template_generator,
                                  project_name=self.__project_name,
                                  output_dir=self.__output_dir)
        checksum_path = create_checksum(strings_paths=localisables,
                                        filename=CHECKSUM_FILENAME,
                                        output_dir=self.__output_dir)

        file_paths = {
            FilepathKey.enums: enum_paths, 
            FilepathKey.stringsdict: localisables[1],
            FilepathKey.strings: localisables[0], 
            FilepathKey.checksum: checksum_path,
            FilepathKey.csv: files if not skip_csv_generation else []
        }

        return file_paths

    def copy_files(self, paths_to_copy: dict):
        """
        Copies all the files generated to the project directory.
        """
        if not self.__project_dir:
            print("Skipping xcode file copy, missing path")
            return
        csv_path = paths_to_copy[FilepathKey.csv]
        enum_path = paths_to_copy[FilepathKey.enums]
        stringsdict_path = paths_to_copy[FilepathKey.stringsdict]
        strings_path = paths_to_copy[FilepathKey.strings]
        checksum_path = paths_to_copy[FilepathKey.checksum]
        copy_xcode_files(csv_path, enum_path, stringsdict_path, strings_path, checksum_path, self.__project_dir)
