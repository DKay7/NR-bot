import logging
import gspread

from utils.db_api.db import db


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

        logger.debug('CONNECTING TO SSP ENDED')

        self.status_to_str = {
            0: "Поиск",
            1: "Назначен мастер",
            2: "Выполнен",
            3: "Не договорились",
            4: "Висяк",
            5: "Архив"
        }

        self.status_to_color = {
            0: (0, 0, 0),
            1: (56, 118, 29),
            2: (230, 145, 56),
            3: (166, 77, 121),
            4: (109, 158, 235),
            5: (234, 67, 53),
        }

        logger.debug('UPDATED SSP STARTED')
        for ticket in db.tickets.find():
            self.update_table(ticket)

        logger.debug('UPDATED SSP ENDED')

    # TODO optimize!!! search not for all tickets, but for exact codes!
    def update_table(self, ticket):
        tid = ticket['id']
        target_range, target_row = self.get_target_range(tid)
        new_data = self.get_data(ticket)

        logger.debug(f"\n\n{ticket}\n\n")

        # TODO status color
        # TODO formatting
        self.worksheet.update(target_range, new_data)
        self.format_worksheet(ticket, target_row)

    def get_data(self, ticket):
        master_f = get_master_by_name(ticket['master'])
        master_uid = master_f['uid'] if master_f is not None else "Не назначен"
        status = self.status_to_str.get(ticket['status'], ticket['status'])

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

        return data

    def get_target_range(self, tid):
        try:
            target_row = self.worksheet.find(query=str(tid), in_column=1).row

        except (gspread.exceptions.CellNotFound, StopIteration):
            target_row = len(self.worksheet.col_values(1)) + 1

        range_ = f"A{target_row}:N{target_row}"

        return range_, target_row

    def format_worksheet(self, ticket, target_row):
        color = self.status_to_color[ticket['status']]

        self.worksheet.format(f"N{target_row}",
                              {"backgroundColor": {
                                  "red": color[0],
                                  "green": color[1],
                                  "blue": color[2]
                                }})
