import unittest
from unittest.mock import patch
from datetime import date
from tempfile import gettempdir
from os import path, remove
import filecmp

from localisation.output.enum_builder import output_enums
from localisation.output.template_helper import TemplateGenerator
from localisation.output.csv_builder import build_localisations
from localisation.parser.sheet_parser import parse, LocalisationRow, Argument


# localisations: List[LocalisationRow],
#                  template_generator: TemplateGenerator,
#                  project_name: str,
#                  output_dir: str

class TestEnumBuilder(unittest.TestCase):

    def testOutputtingEnum(self):
        # Mocks the "today()" function inside the template_helper to return a fixed date.
        with patch('localisation.output.template_helper.date') as mock_date:
            mock_date.today.return_value = date(2020, 1, 15)
            mock_date.side_effect = lambda *args, **kw: date(*args, **kw)

            generator = TemplateGenerator()
            temp_dir = gettempdir()
            arguments = [
                Argument(replace_key="${a}", language="en", values={"one": "one", "few": "few", "many": "many"}),
            ]
            localisations = [
                LocalisationRow(key="key.something.test", language="en", translation='A or b ${a}', arguments=arguments),
                LocalisationRow(key="key2.something.test2", language="en", translation="A or b ${a}", arguments=[]),
                LocalisationRow(key="key3.something.test3", language="en", translation="A or b ${a} and c", arguments=arguments),
                LocalisationRow(key="key4.something.test4", language="en", translation="A or b a", arguments=[]),
            ]

            enum_file = output_enums(localisations, generator, "TestName", temp_dir)
            expected_swift = "./test/resources/ExpectedEnum.swift"

            self.assertTrue(filecmp.cmp(enum_file, expected_swift))

            # If the test fails the file won't be removed, so beware of that.
            remove(enum_file)

    def __remove_comments_from_file(self, filename: str):
        with open(filename, "r+") as f:
            d = f.readlines()
            f.seek(0)
            for i in d:
                if not i.startswith("//"):
                    f.write(i)
            f.truncate()