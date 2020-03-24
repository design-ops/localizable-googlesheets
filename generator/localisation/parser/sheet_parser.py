
from dataclasses import dataclass
from typing import Dict, List
from enum import IntEnum
import json

from localisation import PLURAL_KEYS_VALUE

PLURAL_LANGUAGE_KEY = "LANG"

@dataclass
class Argument:
    replace_key: str
    language: str
    values: Dict[str, str]

@dataclass
class LocalisationRow:
    key: str
    language: str
    translation: str
    arguments: List[Argument] # Will only be available if this is a `plural`


def parse(validated_dicts, plurals):
    """
    Parses a set of dictionaries and plurals into a list of LocalisationRow objects.
    """
    arguments = []

    # Get the number of variables
    items_count = len(plurals.get(PLURAL_KEYS_VALUE, []))
    for x in range(items_count):
        # For each key in the plurals dictionary, go through its array based on the index from the number of variables
        arg = Argument(replace_key=plurals.get(PLURAL_KEYS_VALUE)[x], language=plurals.get(PLURAL_LANGUAGE_KEY)[x], values={})
        values = {}
        for key, value in filter(lambda k: (k[0] != PLURAL_KEYS_VALUE and k[0] != PLURAL_LANGUAGE_KEY), plurals.items()):
            if value[x:]:
                values[key.lower()] = value[x]
        arg.values = values
        arguments.append(arg)

    rows = []
    for language, translations in validated_dicts.items():
        for key, translation in translations.items():
            arguments_for_key = list(filter(lambda arg: arg.replace_key in translation and arg.language == language, arguments))
            row = LocalisationRow(key=key, language=language, translation=translation, arguments=arguments_for_key)
            rows.append(row)

    return rows
  