from os import path
import re
from typing import List, Dict, Optional, Tuple

from localisation.utils import create_file
from localisation.output.template_helper import TemplateGenerator
from localisation.parser.sheet_parser import LocalisationRow


def output_enums(localisations: List[LocalisationRow],
                 template_generator: TemplateGenerator,
                 project_name: str,
                 output_dir: str) -> str:
    """
    Outputs all the enums for the localisations, from the given CSV list of dicts, from which
    it builds a dictionary where the key == namespace (str), values == each case (list[str])

    :param localisation: The array of localisation rows from which the enums will be generated.
                         Should correspond to the input file.
    """

    # Build an easier dict to work with for the enums
    enum_dict = __build_enum_dict(localisations=localisations)

    project_dict = {key: enum_dict[key] for key in enum_dict.keys()}
    return __output_enum(dict=project_dict, template_generator=template_generator, project_name=project_name, output_dir=output_dir)


def __output_enum(dict: Dict[str, Dict[str, List[str]]], template_generator: TemplateGenerator, project_name: str, output_dir: str) -> str:
    """
    Outputs an enum file from a dictionary
    :param dict: A dictionary where each key is an enum, and the value is a list with all the cases for said enum
    :returns: The path to the written enum
    """
    filename = "{}Localizations.swift".format(project_name)
    with create_file(output_dir=path.join(output_dir, "enums"),
                    filename=filename) as f:

        enums = []
        for enum_key in sorted(dict.keys()):
            cases = []
            for case in sorted(dict[enum_key].keys()):
                final: str = case + '(' + ", ".join(
                    ["{}: String".format(__underscore_to_camelcase(argument)) for argument in dict[enum_key][case]]) + ')' if dict[enum_key][case] else case
                cases.append({
                    'case_name': final,
                    'identifier_lint': True if len(case) < 3 or len(case) > 40 else False
                })

            enum_name = "".join([name[0].upper() + name[1:] for name in enum_key.split(".")])
            enums.append({
                'name': enum_name,
                'enum_name_lint': True if len(enum_name) > 29 else False,  # 29 + len("Localizable") = 40
                'namespace': enum_key,
                'case': cases
            })

        file = template_generator.generate_enums(filename=filename,
                                                 project_name=project_name,
                                                 enums=enums)
        f.write(file)
        return path.realpath(f.name)


def __build_enum_dict(localisations: List[LocalisationRow]) -> Dict[str, Dict[str, List[str]]]:
    """
    returns something like...
    {
	    'namespace': {
		    'logoutConfirmationAlertTitle': ['arg1'],
		    'logoutConfirmationNoOptionTitle': [],
		    'logoutConfirmationYesOptionTitle': ['arg1', 'arg2']
        }
    }
    """
    enum_dict = dict()
    for localisation in localisations:
        key = localisation.key
        args = __args_in_translation(localisation.translation)
        res = __get_namespace_case_from_key(key)
        if not res:
            continue
        else:
            namespace, case = res

        if namespace not in enum_dict:
            enum_dict[namespace] = {}

        # The following works because we want to use the `other` plural as the default one for arguments
        # Since `other` plural is at the bottom of the enum, it'll be the last one going through this for each key
        enum_dict[namespace][case] = args if args else []

    return enum_dict

def __args_in_translation(translation) -> List[str]:
    return re.findall('\${(.+?)}', translation)


def __get_namespace_case_from_key(key: str) -> Optional[Tuple[str, str]]:
    """
    From a localisation key, returns the namespace and case.
    The namespace is everything until the last '.', and the case is eveything after.

    :param key: The localisation key, which has the format: "A.B.C.D", with undefined length
    :return: A tuple with the namespace and the key, or None if the key doesn't follow the required format
    """
    split_key = key.split(".")
    if len(split_key) < 2:
        return None
    return ".".join(split_key[:-1]), split_key[-1]

def __underscore_to_camelcase(value):
    lower_first = lambda s: s[:1].lower() + s[1:] if s else ''
    return lower_first(''.join(word.title() if i else word for i, word in enumerate(value.split('_'))))