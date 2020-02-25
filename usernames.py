from datetime import datetime, timedelta
from time import sleep

import xlrd
import xlsxwriter

import scr_hlp


class CustomException(Exception):
    pass


class Users:
    row_num = 1
    proxy_row_num = 1
    filename = "usernames.xlsx"
    wb = None
    ws = None
    headers = ["username", "password", "totalvisits"]
    visitslimit = 200

    @staticmethod
    def get_credentials(count_visit):
        wait = False
        filename = Users.filename
        scr_hlp.scr_hlp.print_if_DEBUG("Opening an existing sheet named = %s" % filename)
        wbRD = xlrd.open_workbook(filename)
        sheet = wbRD.sheets()[0]

        Users.wb = xlsxwriter.Workbook(filename)
        ws = Users.ws = Users.wb.add_worksheet(sheet.name)
        if not Users.row_num < sheet.nrows:
            wait = True
            Users.row_num = 1

        lastvisit = sheet.cell(Users.row_num, 3).value
        time_diff = (datetime.strptime(lastvisit, "%Y-%m-%d %H:%M:%S.%f") + timedelta(days=1)) - datetime.now()
        if count_visit:
            scr_hlp.scr_hlp.pause_if_EXTRADEBUG(
                f"({datetime.strptime(lastvisit, '%Y-%m-%d %H:%M:%S.%f')}"
                f" + {timedelta(days=1)}) - {datetime.now()}"
                f"= {time_diff}")

        if lastvisit != "" and time_diff.days == 0:
            if wait:
                print(f"All users reached to their limits. Applied wait for {time_diff.total_seconds()} seconds."
                      f"\nShould be end at {datetime.now() + time_diff}")
                sleep(time_diff.total_seconds())
                totalvisits = 0
            else:
                totalvisits = int(sheet.cell(Users.row_num, 2).value)
        else:
            totalvisits = 0
        if not totalvisits < Users.visitslimit:
            scr_hlp.scr_hlp.print_if_DEBUG(
                f"This user has reached its limit. Total visits {totalvisits}. Trying other user.")
            Users.row_num += 1
            if scr_hlp.scr_hlp.useproxy:
                scr_hlp.scr_hlp.initialize_browser_setup()
                raise CustomException("No need to continue the caller function.")
            else:
                return Users.get_credentials(count_visit)

        for row in range(sheet.nrows):
            for col in range(sheet.ncols):
                ws.write(row, col, sheet.cell(row, col).value)
        if count_visit:
            ws.write(Users.row_num, 2, totalvisits + 1)
            ws.write(Users.row_num, 3, str(datetime.now()))
        else:
            ws.write(Users.row_num, 2, totalvisits)
            ws.write(Users.row_num, 3, lastvisit)
        Users.wb.close()
        uname = sheet.cell(Users.row_num, 0).value
        passw = sheet.cell(Users.row_num, 1).value
        if count_visit:
            scr_hlp.scr_hlp.pause_if_EXTRADEBUG(
                f"Username = {uname}\t pass = {passw}\t total visits = {totalvisits + 1}")
        return uname, passw
