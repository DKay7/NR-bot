import logging

import httplib2
import apiclient.discovery
from utils.db_api.db import db
from oauth2client.service_account import ServiceAccountCredentials

import gspread

from utils.db_api.db_commands import get_master_by_name


logger = logging.getLogger('ssp_logger')
logger.setLevel(logging.DEBUG)


class Spreadsheets:
    def __init__(self):
        logger.debug('CONNECTING TO SSP STARTED')

        self.CREDENTIALS_FILE = 'python-application-bot-43a8a35cc985.json'

        self.gc = gspread.service_account(filename=self.CREDENTIALS_FILE)
        self.sheet = self.gc.open_by_key('1ovwFjKZgGGsUj3FWMhM8D1YNWvfdPahZPBldAX_NnJk')
        self.worksheet = self.sheet.sheet1

        logger.debug('CONNECTING TO SSP END')

        self.status_to_str = {
            0: "Поиск",
            1: "Назначен мастер",
            2: "ВЫполнен",
            3: "Не договорились",
            4: "Висяк",
            5: "Архив"
        }

        self.update_table()
        logger.debug('UPDATED SSP END')

    def update_table(self):
        # TODO update to 2 to delete existing rows.
        last_row = 6

        # TODO optimize!!! search not for all tickets, but for exact codes!
        for ticket in db.tickets.find():
            range_ = f"A{last_row}:N{last_row}"

            master_f = get_master_by_name(ticket['master'])
            master_uid = master_f['uid'] if master_f is not None else "Не назначен"

            status = self.status_to_str.get(ticket['status'], ticket['status'])

            logger.debug(f"\n\n{ticket}\n\n")

            # TODO status color
            # TODO formatting
            data = [
                [
                     str(ticket['id']),
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

            self.worksheet.update(range_, data)

            last_row += 1
