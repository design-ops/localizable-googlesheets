import unittest
from unittest.mock import patch
from tempfile import gettempdir
from datetime import date
from os import path, remove
import filecmp

from localisation.output.stringsfile_builder import output_localisable_strings
from localisation.output.template_helper import TemplateGenerator
from localisation.output.csv_builder import build_localisations
from localisation.parser.sheet_parser import LocalisationRow, Argument


class TestStringsfileBuilder(unittest.TestCase):

    def test_output_localisable_strings(self):

        # Mocks the "today()" function inside the template_helper to return a fixed date.
        with patch('localisation.output.template_helper.date') as mock_date:
            mock_date.today.return_value = date(2020, 1, 15)
            mock_date.side_effect = lambda *args, **kw: date(*args, **kw)

            generator = TemplateGenerator()
            temp_dir = gettempdir()
            arguments = [
                Argument(replace_key="__a__", language="en", values={"one": "one", "few": "few", "many": "many"}),
            ]
            localisations = [
                LocalisationRow(key="key", language="en", translation="A or b __a__", arguments=arguments),
                LocalisationRow(key="key2", language="en", translation="A or b __a__", arguments=[]),
                LocalisationRow(key="key3", language="en", translation="A or b __a__ and c", arguments=arguments),
                LocalisationRow(key="key4", language="en", translation="A or b a", arguments=[]),
            ]
            strings_files, stringsdict_files = output_localisable_strings(localisations, template_generator=generator, output_dir=gettempdir(), project_name="TestName")

            for language, filepath in stringsdict_files.items():
                expected_file = f'./test/resources/stringsdicts/{language}.Localizable.stringsdict'
                self.assertTrue(filecmp.cmp(filepath, expected_file))
                remove(filepath)

            for language, filepath in strings_files.items():
                expected_file = f'./test/resources/strings/{language}.localizable.strings'
                self.assertTrue(filecmp.cmp(filepath, expected_file))
                remove(filepath)
 
    def __remove_comments_from_file(self, filename: str):
        with open(filename, "r+") as f:
            d = f.readlines()
            f.seek(0)
            for i in d:
                if not i.startswith("//"):
                    f.write(i)
            f.truncate()