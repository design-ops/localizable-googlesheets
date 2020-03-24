
from itertools import zip_longest
from typing import List, Dict
from dataclasses import dataclass, field


@dataclass
class MissingValue:
    localisation: str
    key: str


@dataclass
class ValidationResult:
    result: Dict[str, Dict[str, str]] = field(default_factory=dict)
    missing_keys: List[str] = field(default_factory=list)
    missing_values: List[MissingValue] = field(default_factory=list)


def validate(localisation: str, localisation_keys: List[str], localisation_values: List[str]) -> ValidationResult:
        """
        Validates the localisation data - keys and values - printing any error to stdout.
        An error could be a missing key and/or value, or leading/trailing \" for values
        Returns a dict with the valid keys and values

        :param localisation: The locale we're localising
        :param localisation_keys: An array of strings with all the localisation keys
        :param localisation_values: An array of strings with all the localised values
        """
        ret = ValidationResult()
        for key, value in zip_longest(localisation_keys, localisation_values):
            if not key and not value:
                continue
            elif not key:
                ret.missing_keys.append(value)
            elif not value:
                ret.missing_values.append(MissingValue(localisation=localisation, key=key))
            else:
                # Remove `-` and snakeCase the string
                if "-" in key:
                    key = __to_swift_standard(key)

                validated_value = __validate_value(key, value)
                ret.result[key] = validated_value 

        return ret


def validate_plurals(plurals):
    """
    Removes trailing new lines from the values
    """
    validated = {}
    for key, value in plurals.items():
        validated[key] = [plural.rstrip("\n\r") for plural in value]
    return validated


def __to_swift_standard(str: str) -> str:
    str = "".join([x.capitalize() for x in str.split('-')])
    return str[0].lower() + str[1:]


def __validate_value(key: str, value: str) -> str:
    if value[-1] == '\"' and value[-2] != '\\':
        print("Found not-escaped trailing \" for key {} in value {} - removing! ".format(key, value))
        return value[:-1]
    elif value[0] == '\"':
        print("Found leading \" for key {} in value {} - removing! ".format(key, value))
        return value[1:]
    elif '\"' in value:
        print("Found \" for key {} in value {} - this could be a mistake".format(key, value))
        return value
    else:
        return value