from datetime import date
import re
from pybars import Compiler
from typing import List, Optional

from localisation.parser.sheet_parser import LocalisationRow


class TemplateGenerator:
    HEADER_TEMPLATE = """//
//  {{filename}}
//  {{project_name}}
//
//  THIS FILE IS GENERATED, DO NOT EDIT IT!
//
"""

    ENUM_TEMPLATE = """{{header}}
import LocalizableGoogleSheets
{{#each enum}}{{#if enum_name_lint}}

//swiftlint:disable:next type_name{{/if}}
enum {{name}}Localizable: Localizable {
    static let localizationNamespace = "{{namespace}}"
{{#each case}}
    case {{case_name}}{{#if identifier_lint}} //swiftlint:disable:this identifier_name{{/if}}
{{/each}}
}
{{/each}}"""

    STRINGSDICT_TEMPLATE = """<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>{{#each plural_template}}
    {{{plural}}}{{/each}}
</dict>
</plist>"""

    PLURAL_TEMPLATE = """<key>{{key_name}}</key>
<dict>
    <key>NSStringLocalizedFormatKey</key>
    <string>{{variable_string}}</string>
    {{{variable_templates}}}
</dict>"""

    VARIABLES_TEMPLATE = """{{#each variables}}<key>{{variable_name}}</key>
    <dict>
        <key>NSStringFormatSpecTypeKey</key>
        <string>NSStringPluralRuleType</string>
        <key>NSStringFormatValueTypeKey</key>
        <string>d</string>{{#each plural_types}}
        <key>{{plural_name}}</key>
        <string>{{plural_value}}</string>{{/each}}
    </dict>{{/each}}"""

    def __init__(self):
        self.__compiler = Compiler()
        self.__header_template = self.__compiler.compile(TemplateGenerator.HEADER_TEMPLATE)
        self.__enum_template = self.__compiler.compile(TemplateGenerator.ENUM_TEMPLATE)
        self.__stringsdict_template = self.__compiler.compile(TemplateGenerator.STRINGSDICT_TEMPLATE)
        self.__plurals_template = self.__compiler.compile(TemplateGenerator.PLURAL_TEMPLATE)
        self.__variables_template = self.__compiler.compile(TemplateGenerator.VARIABLES_TEMPLATE)

    def generate_header(self, filename: str, project_name: str) -> str:
        """
        Generates the header for the files.
        """
        return self.__header_template({'filename': filename,
                                       'project_name': project_name,
                                       'date_created': str(date.today())})

    def generate_enums(self, filename: str, project_name: str, enums: List[dict]) -> str:
        """
        Generates the string for the enums file
        """
        source = {
            'header': self.generate_header(filename, project_name),
            'enum': enums
        }

        return self.__enum_template(source)

    def generate_stringsdict(self, plurals: List[str], filename: str, project_name: str) -> str:
        """
        Generates the content for the stringsdict file.
        """
        source = {
            'header': self.generate_header(filename, project_name),
            'plural_template': [{"plural": plural} for plural in plurals]
        }
        return self.__stringsdict_template(source)

    def generate_strings(self, rows: List[LocalisationRow], filename: str, project_name: str) -> str:
        """
        Generates the content of the strings file.
        """
        header = f"/*\n{self.generate_header(filename, project_name)}*/\n"
        return header + "\n".join([f'"{row.key}" = "{row.translation.replace("${", "__").replace("}", "__")}";' for row in rows])

    def generate_plural(self, key_name: str, variable_string: str, variables: Optional[str]) -> str:
        """
        Generates the plural xml for the stringsdict template
        """
        template_dict = {
            "key_name": key_name,
            "variable_string": variable_string
        }

        if variables is not None:
            template_dict["variable_templates"] = variables

        return self.__plurals_template(template_dict)

    def generate_variables(self, variables) -> str:
        """
        Generates the variables xml to be used in the stringsdict template
        """
        return self.__variables_template({"variables": variables})

