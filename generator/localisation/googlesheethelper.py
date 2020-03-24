import os
import pickle
from typing import NewType, TypeVar, Tuple, Optional, Dict

from googleapiclient.discovery import build, Resource
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

SheetRef = TypeVar("SheetRef", str, int)

SheetRange = NewType("SheetRange", Tuple[SheetRef, SheetRef])
A1NotationRange = NewType("A1NotationRange", str)


class GoogleSheetHelper:

    def __init__(self, scopes: [str], credentials: str, spreadsheet_id: str, sheet_name: str, plurals_sheet_name: Optional[str] = None):
        self.__scopes = scopes
        self.__credentials = credentials
        self.__spreadsheet_id = spreadsheet_id
        self.__sheet_name = sheet_name
        self.__plurals_sheet_name = plurals_sheet_name
        self.__service = None

    def __build_sheets_service(self) -> Resource:
        """
        Builds the GoogleSheets service with the class scopes
        :return:
        """
        creds = None
        cache_path = os.path.join(os.path.dirname(__file__), '../resources/cache.pickle')
        credentials_path = self.__credentials

        if not os.path.exists(credentials_path):
            exit("🚨 ERROR 🚨 Please ensure credentials exists at generator/resources/credentials.json and try again.")

        if os.path.exists(cache_path):
            with open(cache_path, 'rb') as token:
                creds = pickle.load(token)
        # If there are no (valid) credentials available, let the user log in.
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(credentials_path, self.__scopes)
                creds = flow.run_console()
            # Save the credentials for the next run
            with open(cache_path, 'wb') as token:
                pickle.dump(creds, token)

        service = build('sheets', 'v4', credentials=creds)
        return service

    def get_a1_notation_from_sheet_range(self, sheet_name: str, sheet_range: SheetRange) -> A1NotationRange:
        """
        Returns a A1NotationRange from a SheetRange
        """
        return A1NotationRange("'{}'!{}:{}".format(sheet_name, sheet_range[0], sheet_range[1]))

    def get_range(self, sheet_name: str, start_at: SheetRef, end_at: Optional[SheetRef] = None) -> A1NotationRange:
        """
        Returns a A1NotationRange spawning from two rows.
        The second one is optional
        """
        sheet_range = SheetRange((start_at, end_at if end_at is not None else start_at))

        return self.get_a1_notation_from_sheet_range(sheet_name=sheet_name, sheet_range=sheet_range)

    def get_values(self, start_at: SheetRef, end_at: Optional[SheetRef] = None) -> Dict:
        return self._get_values(sheet_name=self.__sheet_name, start_at=start_at, end_at=end_at)

    def get_plurals_values(self, start_at: SheetRef, end_at: Optional[SheetRef] = None) -> Dict:
        """
        Gets the plurals values from the spreadsheet.
        If there is no plurals spreadsheet defined, simply returns an empty dictionary.
        """
        if self.__plurals_sheet_name is None:
            return {}
        return self._get_values(sheet_name=self.__plurals_sheet_name, start_at=start_at, end_at=end_at)

    def _get_values(self, sheet_name: str, start_at: SheetRef, end_at: Optional[SheetRef] = None) -> Dict:
        """
        Returns all the values for a given Row Range
        :param start_at: The reference of the sheet where the fetching should start. This can be a cell, row, or column.
        :param start_at: The referect of the sheet where the fetching should end. This can be a cell, row, or column.
        If it's null, the start_at value will be used.

        :return: A dictionary with the fetched values
        """

        if not self.__service:
            self.__service = self.__build_sheets_service()

        range = self.get_range(sheet_name=sheet_name, start_at=start_at, end_at=end_at)

        result = self.__service.spreadsheets().values().get(spreadsheetId=self.__spreadsheet_id, range=range)
        response = result.execute()
        return response["values"]
