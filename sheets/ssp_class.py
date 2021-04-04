import logging

import httplib2
import apiclient.discovery
from utils.db_api.db import db
from oauth2client.service_account import ServiceAccountCredentials

from utils.db_api.db_commands import get_master_by_name


logger = logging.getLogger('ssp_logger')
logger.setLevel(logging.DEBUG)


class Spreadsheets:
    def __init__(self):
        logger.debug('CONNECTING TO SSP STARTED')

        self.CREDENTIALS_FILE = 'python-application-bot-43a8a35cc985.json'
        self.credentials = ServiceAccountCredentials.from_json_keyfile_name(self.CREDENTIALS_FILE,
                                                                            ['https://www.googleapis.com/auth/spreadsheets',
                                                                             'https://www.googleapis.com/auth/drive'])

        self.httpAuth = self.credentials.authorize(httplib2.Http())
        self.service = apiclient.discovery.build('sheets', 'v4', http=self.httpAuth)
        self.spreadsheetID = "1ovwFjKZgGGsUj3FWMhM8D1YNWvfdPahZPBldAX_NnJk"

        logger.debug('CONNECTING TO SSP END')

        self.status_to_str = {
            0: "Поиск",
            1: "Назначен мастер",
            2: "Не договорились",
            3: "Висяк",
            4: "Архив"
        }

        self.update_table()
        logger.debug('UPDATED SSP END')

    def update_table(self):
        # TODO update to 2 to delete existing rows.
        last_row = 6

        # TODO optimize!!! search not for all tickets, but for exact codes!
        for ticket in db.tickets.find():
            range_ = f"Лист1!A{last_row}:N{last_row}"

            master_f = get_master_by_name(ticket['master'])
            master_uid = master_f['uid'] if master_f is not None else "Не назначен"

            status = self.status_to_str.get(ticket['status'], ticket['status'])

            # TODO status color
            # TODO formatting
            data = [
                [
                     str(ticket['_id']),
                     str(ticket['create_date']),
                     str(ticket['confirm_date']),
                     str(ticket['accept_date']),
                     str(ticket['address']),
                     str(ticket['number']),
                     str(ticket['name']),
                     str(ticket['category']),
                     str(ticket['desc']),
                     str(ticket['price']),
                     str(ticket['master']),
                     str(master_uid),
                     str(status),
                ]
            ]

            self.service.spreadsheets().values().batchUpdate(spreadsheetId=self.spreadsheetID,
                                                             body={
                                                                "valueInputOption": "USER_ENTERED",
                                                                "data": [
                                                                    {"range": range_,
                                                                     "majorDimension": "ROWS",
                                                                     "values": data}
                                                                ]
                                                                }).execute()

            last_row += 1
