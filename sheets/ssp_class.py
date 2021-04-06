import logging
import gspread
from utils.db_api.db import db
from utils.db_api.db_commands import get_master_by_name


logger = logging.getLogger('ssp_logger')
logger.setLevel(logging.DEBUG)


class Spreadsheets:
    def __init__(self):
        logger.info('CONNECTING TO SSP STARTED')

        # Take secret file
        self.CREDENTIALS_FILE = 'python-application-bot-43a8a35cc985.json'

        # Connect to spreadsheet and choose page-1
        self.gc = gspread.service_account(filename=self.CREDENTIALS_FILE)
        self.sheet = self.gc.open_by_key('1-GGLXre9pvZlu4IEttGxyz09lh31YATP_Q06Z_hO9UU')
        self.worksheet = self.sheet.sheet1

        logger.info('CONNECTING TO SSP ENDED')

        # Status code - Str
        self.status_to_str = {
            0: "Поиск",
            1: "Назначен мастер",
            2: "Выполнен",
            3: "Не договорились",
            4: "Висяк",
            5: "Архив"
        }

        # Status code - Color (R, G, B)
        self.status_to_color = {
            0: (0, 0, 0),
            1: (51, 51, 255),
            2: (50, 205, 50),
            3: (62, 69, 50),
            4: (255, 244, 79),
            5: (11, 218, 81),
        }

        logger.info('SSP UPDATE STARTED')
        
        # Update all ssp when bot is starting
        for ticket in db.tickets.find():
            self.update_table(ticket=ticket, table='tickets')

        for master in db.masters.find():
            self.update_table(master=master, table='masters')

        logger.info('SSP UPDATE ENDED')

    # Updates only one row for target ticket
    def update_table(self, table, ticket=None, master=None):

        assert table in ['tickets', 'masters']

        if table == 'tickets':
            assert ticket is not None

            self.worksheet = self.sheet.get_worksheet(0)
            tid = ticket['id']
            target_range, target_row = self.get_target_range(tid)
            new_data = self.get_data(ticket=ticket)

            logger.debug(f"\nTICKET:\n{ticket}\n\n")

            self.worksheet.update(target_range, new_data)
            self.format_tickets_worksheet(ticket, target_row)

        if table == 'masters':
            assert master is not None

            self.worksheet = self.sheet.get_worksheet(1)
            mid = master['id']
            target_range, _ = self.get_target_range(mid, for_='masters')
            new_data = self.get_data(master=master, for_='master')

            logger.debug(f"\nMASTER:\n{master}\n\n")
            self.worksheet.update(target_range, new_data)

    def delete_master(self, master):
        self.worksheet = self.sheet.get_worksheet(1)

        mid = master['id']
        target_row = self.worksheet.find(query=str(mid), in_column=1).row
        target_range = f"A{target_row}:F{target_row}"

        # TODO make it the right way
        # F - A = 6
        new_data = [[''] * 6]
        self.worksheet.update(target_range, new_data)

    def get_data(self, ticket=None, master=None, for_='ticket'):

        assert for_ in ['ticket', 'master']

        if for_ == 'ticket':
            assert ticket is not None
            master_f = get_master_by_name(ticket['master'])
            master_uid = master_f['uid'] if master_f is not None else "Не назначен"
            status = self.status_to_str.get(ticket['status'], ticket['status'])

            data = [
                [
                    str(ticket['id']),
                    str(ticket['create_date']),
                    str(ticket['accept_date']),
                    str(ticket['confirm_date']),
                    str(ticket['address']),
                    str(ticket['number']),
                    str(ticket['name']),
                    str(ticket['category']),
                    str(ticket['desc']),
                    str(ticket['price']),
                    str(ticket['final_price']),
                    str(ticket['master']),
                    str(master_uid),
                    str(status),
                ]
            ]

            return data

        elif for_ == 'master':
            assert master is not None

            data = [
                [
                    str(master['id']),
                    str(master['speciality']),
                    str(master['name']),
                    str(master['phone']),
                    str(master['username']),
                    str(master['address'])
                ]
            ]

            return data

    def get_target_range(self, id_, for_='tickets'):
        assert for_ in ['tickets', 'masters']

        try:
            target_row = self.worksheet.find(query=str(id_), in_column=1).row

        except (gspread.exceptions.CellNotFound, StopIteration):
            target_row = len(self.worksheet.col_values(1)) + 1

        if for_ == 'tickets':
            range_ = f"A{target_row}:O{target_row}"
            return range_, target_row

        elif for_ == 'masters':
            range_ = f"A{target_row}:F{target_row}"
            return range_, target_row

    def format_tickets_worksheet(self, ticket, target_row, color=None):

        if color is None:
            color = self.status_to_color[ticket['status']]

            self.worksheet.format(f"N{target_row}",
                                  {"backgroundColor": {
                                      "red": color[0] / 255,
                                      "green": color[1] / 255,
                                      "blue": color[2] / 255
                                    }})

        elif color is not None:
            self.worksheet.format(f"N{target_row}",
                                  {"backgroundColor": {
                                      "red": color[0] / 255,
                                      "green": color[1] / 255,
                                      "blue": color[2] / 255
                                  }})
