import unittest
from datetime import date

from localisation.output.template_helper import TemplateGenerator


class TestTemplateHelper(unittest.TestCase):
    MOCK_HEADER = """//
//  MockFilename
//  MockProjectName
//
//  THIS FILE IS GENERATED, DO NOT EDIT IT!
//
"""

    def setUp(self):
        super().setUp()
        self.__template_helper = TemplateGenerator()

    def test_generate_header(self):
        header = self.__template_helper.generate_header(filename="MockFilename", project_name="MockProjectName")
        self.assertEqual(header, TestTemplateHelper.MOCK_HEADER.format(str(date.today())))

    def test_generate_enum(self):
        mock = """{header}
import LocalizableSheets

enum Enum1Localizable: Localizable {{
    static let localizationNamespace = "Namespace1"

    case Enum1Case1 //swiftlint:disable:this identifier_name
    case Enum1Case2 //swiftlint:disable:this identifier_name
    case Enum1Case3
    case Enum1Case4 //swiftlint:disable:this identifier_name
    case Enum1Case5
}}

enum Enum2Localizable: Localizable {{
    static let localizationNamespace = "Namespace2"

    case Enum2Case1
    case Enum2Case2 //swiftlint:disable:this identifier_name
    case Enum2Case3 //swiftlint:disable:this identifier_name
    case Enum2Case4
    case Enum2Case5
}}

enum Enum3Localizable: Localizable {{
    static let localizationNamespace = "Namespace3"

    case Enum3Case1 //swiftlint:disable:this identifier_name
    case Enum3Case2
    case Enum3Case3
    case Enum3Case4 //swiftlint:disable:this identifier_name
    case Enum3Case5
}}
"""
        enums = [
            {
                'name': "Enum1",
                'namespace': "Namespace1",
                'case': [
                    {"case_name": "Enum1Case1", "identifier_lint": True},
                    {"case_name": "Enum1Case2", "identifier_lint": True},
                    {"case_name": "Enum1Case3", "identifier_lint": False},
                    {"case_name": "Enum1Case4", "identifier_lint": True},
                    {"case_name": "Enum1Case5", "identifier_lint": False},
                ]
            },
            {
                'name': "Enum2",
                'namespace': "Namespace2",
                'case': [
                    {"case_name": "Enum2Case1", "identifier_lint": False},
                    {"case_name": "Enum2Case2", "identifier_lint": True},
                    {"case_name": "Enum2Case3", "identifier_lint": True},
                    {"case_name": "Enum2Case4", "identifier_lint": False},
                    {"case_name": "Enum2Case5", "identifier_lint": False},
                ]
            },
            {
                'name': "Enum3",
                'namespace': "Namespace3",
                'case': [
                    {"case_name": "Enum3Case1", "identifier_lint": True},
                    {"case_name": "Enum3Case2", "identifier_lint": False},
                    {"case_name": "Enum3Case3", "identifier_lint": False},
                    {"case_name": "Enum3Case4", "identifier_lint": True},
                    {"case_name": "Enum3Case5", "identifier_lint": False},
                ]
            }
        ]

        enums_file_str = self.__template_helper.generate_enums("MockFilename", project_name="MockProjectName", enums=enums)

        header = TestTemplateHelper.MOCK_HEADER.format(str(date.today()))

        self.maxDiff = None
        self.assertEqual(enums_file_str, mock.format(header=header))
