import unittest

from localisation.googlesheethelper import GoogleSheetHelper, A1NotationRange, SheetRange


class TestGoogleSheetHelper(unittest.TestCase):

    def setUp(self):
        super().setUp()
        self.sheet_helper = GoogleSheetHelper(scopes="", spreadsheet_id="", sheet_name="mockName")

    def test_get_a1_notation_from_sheet_range(self):
        self.assertEqual(self.sheet_helper.get_a1_notation_from_sheet_range(sheet_name="mockName", sheet_range=SheetRange(("A", "A"))),
                         A1NotationRange("'mockName'!A:A"))
        self.assertEqual(self.sheet_helper.get_a1_notation_from_sheet_range(sheet_name="mockName", sheet_range=SheetRange(("2", "2"))),
                         A1NotationRange("'mockName'!2:2"))
        self.assertEqual(self.sheet_helper.get_a1_notation_from_sheet_range(sheet_name="mockName", sheet_range=SheetRange(("A2", "Z4"))),
                         A1NotationRange("'mockName'!A2:Z4"))

    def test_get_range(self):
        self.assertEqual(self.sheet_helper.get_range(sheet_name="mockName", start_at="A1"),
                         A1NotationRange("'mockName'!A1:A1"))
        self.assertEqual(self.sheet_helper.get_range(sheet_name="mockName", start_at="A1", end_at="Z10"),
                         A1NotationRange("'mockName'!A1:Z10"))
