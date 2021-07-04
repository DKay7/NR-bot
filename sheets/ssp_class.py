import logging
import gspread
import gspread_formatting as gsf
from time import sleep
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
        self.ticket_worksheet = self.sheet.get_worksheet(0)
        self.master_worksheet = self.sheet.get_worksheet(1)

        logger.info('CONNECTING TO SSP ENDED')

        # Status code - Str
        self.ticket_status_to_str = {
            0: "Готов взять заказ",
            1: "В работе",
            2: "Выполнен",
            3: "Мастер договаривается с клиентом",
            4: "Не договорились",
            5: "Архив"
        }

        self.master_status_to_str = {
            0: "Не подтвержден администрацией",
            1: "В строю",
            2: "Отдыхает",
            3: "Уволен"
        }


        # Status code - Color (R, G, B)
        self.ticket_status_to_color = {
            0: (204, 0, 0),
            1: (51, 51, 255),
            2: (50, 205, 50),
            3: (153, 0, 255),
            4: (255, 244, 79),
            5: (108, 108, 108),
        }

        self.master_status_to_color = {
            0: (255, 0, 0),
            1: (51, 255, 51),
            2: (153, 0, 255),
            3: (255, 0, 0)
        }

        logger.info('SSP UPDATE STARTED')
        
        # Update all ssp when bot is starting
        tickets = list(db.tickets.find())
        masters = list(db.masters.find())

        ticket_values = self.sheet.get_worksheet(0).range(f"A1:S{len(tickets)+1}")
        ticket_colors = list()
        masters_values = self.sheet.get_worksheet(1).range(f"A1:J{len(masters)+1}")
        master_colors = list()

        # TODO make function
        cell = 0
        for ticket in tickets:
            new_data = self.get_data(ticket=ticket)[0]

            for data in new_data:
                ticket_values[cell].value = data
                cell += 1

                if ticket_values[cell].address.startswith("N"):
                    color = self.ticket_status_to_color.get(ticket['status'], (255, 255, 255))

                    format = gsf.cellFormat(
                        backgroundColor=gsf.color(color[0]/255, color[1]/255, color[2]/255)
                    )
                    ticket_colors.append((f"N{ticket_values[cell].row}", format))

        # TODO make function 
        cell = 0
        for master in masters:
            new_data = self.get_data(master=master, for_='master')[0]
            for data in new_data:
                masters_values[cell].value = data
                cell += 1

                if masters_values[cell].address.startswith("J"):
                    color = self.master_status_to_color.get(master['status'], (255, 255, 255))

                    format = gsf.cellFormat(
                        backgroundColor=gsf.color(color[0]/255, color[1]/255, color[2]/255)
                    )
                    master_colors.append((f"J{masters_values[cell].row}", format))

        self.ticket_worksheet.update_cells(ticket_values)
        gsf.format_cell_ranges(self.ticket_worksheet, ticket_colors)


        self.master_worksheet.update_cells(masters_values)
        gsf.format_cell_ranges(self.master_worksheet, master_colors)

        logger.info('SSP UPDATE ENDED')

    # Updates only one row for target ticket
    def update_table(self, table, ticket=None, master=None):

        assert table in ['tickets', 'masters']

        if table == 'tickets':
            assert ticket is not None

            tid = ticket['id']
            target_range, target_row = self.get_target_range(tid)
            new_data = self.get_data(ticket=ticket)

            logger.debug(f"\nTICKET:\n{ticket}\n\n")

            self.ticket_worksheet.update(target_range, new_data)
            self.format_tickets_worksheet(ticket, target_row)

        if table == 'masters':
            assert master is not None

            mid = master['id']
            target_range, target_row = self.get_target_range(mid, for_='masters')
            new_data = self.get_data(master=master, for_='master')

            logger.debug(f"\nMASTER:\n{master}\n\n")
            self.master_worksheet.update(target_range, new_data)
            self.format_master_worksheet(master, target_row)

    def delete_master(self, master):
        assert master is not None


        mid = master['id']
        target_row = self.master_worksheet.find(query=str(mid), in_column=1).row
        self.master_worksheet.delete_row(target_row)

    def get_data(self, ticket=None, master=None, for_='ticket'):

        assert for_ in ['ticket', 'master']

        if for_ == 'ticket':
            assert ticket is not None
            master_f = get_master_by_name(ticket['master'])
            master_uid = master_f['uid'] if master_f is not None else "Не назначен"
            ticket_status = self.ticket_status_to_str.get(ticket['status'], ticket['status'])

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
                    str(ticket_status),
                    str(ticket['final_work']),
                    str(ticket['is_client_happy']),
                    str(ticket['denied_0']),
                    str(ticket['denied_1']),
                    str(ticket['denied_2']),
                ]
            ]

            return data

        elif for_ == 'master':
            assert master is not None
            master_status = self.master_status_to_str.get(master['status'], master['status'])

            data = [
                [
                    str(master['id']),
                    str(master['start_date']),
                    str(master['speciality']),
                    str(master['additional_spec']),
                    str(master['name']),
                    str(master['phone']),
                    str(master['username']),
                    str(master['uid']),
                    str(master['address']),
                    str(master_status)
                ]
            ]

            return data

    def get_target_range(self, id_, for_='tickets'):
        assert for_ in ['tickets', 'masters']
        
        worksheet = self.ticket_worksheet if for_=="tickets" else self.master_worksheet

        try:
            target_row = worksheet.find(query=str(id_), in_column=1).row

        except (gspread.exceptions.CellNotFound, StopIteration):
            target_row = len(worksheet.col_values(1)) + 1

        if for_ == 'tickets':
            range_ = f"A{target_row}:S" \
                     f"{target_row}"
            return range_, target_row

        elif for_ == 'masters':
            range_ = f"A{target_row}:J{target_row}"
            return range_, target_row

    def format_tickets_worksheet(self, ticket, target_row, color=None):

        if color is None:
            color = self.ticket_status_to_color.get(ticket['status'], (255, 255, 255))

            self.ticket_worksheet.format(f"N{target_row}",
                                          {"backgroundColor": {
                                              "red": color[0] / 255,
                                              "green": color[1] / 255,
                                              "blue": color[2] / 255
                                              }})

        elif color is not None:
            self.ticket_worksheet.format(f"N{target_row}",
                                  {"backgroundColor": {
                                      "red": color[0] / 255,
                                      "green": color[1] / 255,
                                      "blue": color[2] / 255
                                  }})

    def format_master_worksheet(self, master, target_row, color=None):

        if color is None:
            color = self.master_status_to_color.get(master['status'], (255, 255, 255))
            
            self.master_worksheet.format(f"J{target_row}",
                                          {"backgroundColor": {
                                              "red": color[0] / 255,
                                              "green": color[1] / 255,
                                              "blue": color[2] / 255
                                              }})

        elif color is not None:
            self.master_worksheet.format(f"J{target_row}",
                                  {"backgroundColor": {
                                      "red": color[0] / 255,
                                      "green": color[1] / 255,
                                      "blue": color[2] / 255
                                  }})

    