from __future__ import print_function

import datetime

from googleapiclient import discovery
from googleapiclient.errors import HttpError
import os.path
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
import psycopg2 as pg

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']


def insert_date(SAMPLE_SPREADSHEET_ID, SAMPLE_RANGE_NAME, get):
    """Shows basic usage of the Sheets API.
    Prints values from a sample spreadsheet.
    """
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    try:
        # service = build('sheets', 'v4', credentials=creds)
        service = discovery.build('sheets', 'v4', credentials=creds)
        # How the input data should be interpreted.
        value_input_option = 'USER_ENTERED'

        # How the input data should be inserted.
        insert_data_option = 'OVERWRITE'

        value_range_body = load_date_from_dwh(get)
        request = service.spreadsheets().values().append(spreadsheetId=SAMPLE_SPREADSHEET_ID, range=SAMPLE_RANGE_NAME,
                                                         valueInputOption=value_input_option,
                                                         insertDataOption=insert_data_option, body=value_range_body)
        response = request.execute()
        print(response)
    except HttpError as err:
        print(err)


def load_date_from_dwh(get):
    values = []
    with open("secret/pg-dwh.txt") as file:
        database_info = file.read().replace('\n', ' ')
        with pg.connect(database_info) as dwh:
            with dwh.cursor() as dwh_cursor:
                dwh_cursor.execute(get)
                row = dwh_cursor.fetchone()
                while row is not None:
                    row = list(row)
                    for i in range(len(row)):
                        if isinstance(row[i], list) or isinstance(row[i], datetime.datetime):
                            row[i] = str(row[i])
                    values.append(row)
                    row = dwh_cursor.fetchone()
            return {
                'values': values
            }


if __name__ == '__main__':
    get = "select * from req_ans_priority; "
    SAMPLE_SPREADSHEET_ID = '1DSXYP_L1GLF4jdZWlNBbX_mblyOFOwWFmKTh67pWZsc'
    SAMPLE_RANGE_NAME = 'A:F'
    insert_date(SAMPLE_SPREADSHEET_ID, SAMPLE_RANGE_NAME, get)
    get = "select * from offer; "
    SAMPLE_SPREADSHEET_ID = '1m1zZjEZvKkAqrfrjkHBIKvl5tbS2zi0d-DBt0GSAEcI'
    SAMPLE_RANGE_NAME = 'A:B'
    insert_date(SAMPLE_SPREADSHEET_ID, SAMPLE_RANGE_NAME, get)
    get = "select * from get_worse_response_30_percent; "
    SAMPLE_SPREADSHEET_ID = '1CzCUHFlMUZrV_IJ5K9HSeXkEIcB4tLEVSgWUaulYmU8'
    SAMPLE_RANGE_NAME = 'A:B'
    insert_date(SAMPLE_SPREADSHEET_ID, SAMPLE_RANGE_NAME, get)
