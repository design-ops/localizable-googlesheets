# Set up the command line app
import argparse
from typing import Optional

from googlesheethelper import GoogleSheetHelper
from process_localisation import Localisation
from output.template_helper import TemplateGenerator


SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly']

def main(spreadsheet_id: str,
         sheet_name: str,
         plurals_sheet_name: str,
         credentials: str,
         output_dir: Optional[str],
         project_dir: Optional[str],
         skip_csv: bool = False) -> None:
    
    print('spreadsheet id: {}'.format(spreadsheet_id))
    print('sheet name: {}'.format(sheet_name))
    print('plurals sheet name: {}'.format(plurals_sheet_name))
    print('output dir: {}'.format(output_dir))
    print('project dir: {}'.format(project_dir))
    print('skip csv: {}'.format(skip_csv))

    google_sheet_helper = GoogleSheetHelper(scopes=SCOPES,
                                            credentials=credentials,
                                            spreadsheet_id=spreadsheet_id,
                                            sheet_name=sheet_name,
                                            plurals_sheet_name=plurals_sheet_name)
    template_helper = TemplateGenerator()

    localisation = Localisation(google_sheet_helper, template_helper, output_dir, project_dir)
    paths_written = localisation.localise(skip_csv_generation=skip_csv)
    if paths_written:
        localisation.copy_files(paths_to_copy=paths_written)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--credentials", help="Path to Google Cloud credentials with Google Sheets read permissions")
    parser.add_argument("--sheet-id", help="Id of the spreadsheet to use")
    parser.add_argument("--sheet-name", help="Name of the sheet in the spreadsheet")
    parser.add_argument("--plurals-sheet-name", help="Name of the plurals sheet in the spreadsheet")
    parser.add_argument("--output", help="Output folder")
    parser.add_argument("--project-dir", help="Xcode Project directory")
    parser.add_argument("--skip-csv", action='store_true',
                        help="Skips generation of csv representation and retrieves it instead from project-dir")
    args = parser.parse_args()

    main(args.sheet_id, args.sheet_name, args.plurals_sheet_name, args.credentials, args.output, args.project_dir, args.skip_csv)
