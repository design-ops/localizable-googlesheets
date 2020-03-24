
from os import path
from typing import List
import re

from localisation.parser.sheet_parser import LocalisationRow
from localisation.utils import create_file
from localisation.output.template_helper import TemplateGenerator


def output_localisable_strings(localisations: List[LocalisationRow], template_generator: TemplateGenerator, output_dir: str, project_name: str) -> (dict, dict):
    """
    Outputs the localizable.stringsdict files into the folders
    '{output_dir}/{language_code}/

    :param localisations: The localisations to be created in stringsdict format.
    :return a tuple of dict with the path for the written file, where the key is each language code, e.g.:
    {
        'pt': /path/to/pt.stringsdict,
        'en': /path/to/en.stringsdict
    }

    See: https://developer.apple.com/library/archive/documentation/MacOSX/Conceptual/BPInternational/StringsdictFileFormat/StringsdictFileFormat.html
    """

    # Will store the paths of the written files
    plural_paths = {}
    regular_paths = {}

    # First find all languages in the localisations
    languages = set([row.language for row in localisations])

    # Iterate through the languages we have in the localisations and create a dictionary for each record to be inserted
    # into the plist file. Then, create a new file for the language and write the plist.
    for lang in languages:
        plural_localisation = []
        regular_localisation = []
        for row in localisations:
            if row.language != lang:
                continue

            # Create the record from the localisation and append it to the list of localisations
            if len(row.arguments) == 0:
                regular_localisation.append(row)
            else:
                plist_record = __build_dict(row, template_generator)
                plural_localisation.append(plist_record)

        stringsdict_filename = f"{lang}.Localizable.stringsdict"
        with create_file(path.join(output_dir, lang), stringsdict_filename) as f:
            f.write(template_generator.generate_stringsdict(plural_localisation, stringsdict_filename, project_name))
            plural_paths[lang] = path.realpath(f.name)

        strings_filename = f"{lang}.localizable.strings"
        with create_file(path.join(output_dir, lang), strings_filename) as f:
            f.write(template_generator.generate_strings(regular_localisation, strings_filename, project_name))
            regular_paths[lang] = path.realpath(f.name)

    return (regular_paths, plural_paths)


def __build_dict(localisation, template_generator):
    """
    Builds the plist dictionary for a localisation in stringsdict format.
    """
    variable_string = __build_variable_string(localisation.translation, [arg.replace_key for arg in localisation.arguments])

    variables_list = [__build_argument_dict(arg) for arg in localisation.arguments]
    variable_templates = template_generator.generate_variables(variables_list) if len(variables_list) > 0 else None

    return template_generator.generate_plural(key_name=localisation.key, variable_string=variable_string, variables=variable_templates)


def __build_variable_string(translation, variables) -> str:
    """
    Takes two parameters.
    - translation: the string that will be used as the format in the translation string.
    - variables: a list of variables that are used as replacement strings in the translation string.

    Returns the translation string with the variables formatted in the correct way for the stringsdict file.

    __build_variable_string("This is an ${example}", ["${example}"]) -> "This is an %#@__example__@"
    """
    for variable in variables:
        translation = translation.replace(variable, f"%#@{variable}@")

    translation = translation.replace("${", "__").replace("}", "__")
    return translation


def __build_argument_dict(argument):
    """
    Returns the given argument in a format that can be consumed by the template generator
    """
    return {
        "variable_name": argument.replace_key.replace("${", "__").replace("}", "__"),
        "plural_types": __build_plural_types(argument.values)
    }

def __build_plural_types(plurals):
    """
    Returns the given list of plurals in a format that can be consumed by the template generator
    Input is plurals, a dictionary in the following form:
    
    {'one': 'one topping', 'other': '${ice_cream_toppings} toppings', 'zero': 'no toppings'}
    
    Where the keys match one of the CLDR plural categories ('zero', 'one', 'two', 'few', 'many' or 'other')

    The return for an input as the above would be:
    ```
    [
        {
            'plural_name': 'one'
            'plural_value': 'one topping'
        },
        {
            'plural_name': 'other'
            'plural_value': '%d toppings'
        },
        {
            'plural_name': 'zero'
            'plural_value': 'no toppings'
        }
    ]
    ```
    """
    return [{
        "plural_name": key,
        "plural_value": re.sub('\${.+}', "%d", value) # Substitutes the variable value for the string '%d' because that's what the plist needs.
    } for key, value in plurals.items() if value is not None]
