import xlrd, sys, xlsxwriter
from datetime import datetime
import scr_hlp

class users:
    rownum = 1
    filename = "usernames.xlsx"
    wb = None
    ws = None
    headers = ["username","password","totalvisits"]
    visitslimit = 200
    
    @staticmethod
    def open_username_file():
        scr_hlp.scr_hlp.print_if_DEBUG("Opening %s"%users.filename)
        # users.usersFile = xlrd.open_workbook(users.filename)
    
    @staticmethod
    def get_credentials():
        fname = users.filename
        scr_hlp.scr_hlp.print_if_DEBUG("Opening an existing sheet named = %s"%fname)
        wbRD = xlrd.open_workbook(fname)
        sheet = wbRD.sheets()[0]
        
        users.wb = xlsxwriter.Workbook(fname)
        ws = users.ws = users.wb.add_worksheet(sheet.name)
        if not users.rownum < sheet.nrows:
            print("All Usernames' limit is over. No more usernames are available.\nProgram exiting...")
            sys.exit()
        lastvisit = sheet.cell(users.rownum,3).value
        if lastvisit != "" and datetime.strptime(lastvisit,"%Y-%m-%d").date() == datetime.now().date():
            totalvisits = int(sheet.cell(users.rownum,2).value)
            # lastvisit = datetime.now().date()
        else:
            totalvisits = 0
            # lastvisit = datetime.strptime(lastvisit,"%Y-%m-%d").date()
        # if lastvisit < datetime.now().date():
        #     totalvisits = 0
        # else:   
        #     totalvisits = int(sheet.cell(users.rownum,2).value)
        
        if not totalvisits < users.visitslimit:
            scr_hlp.scr_hlp.print_if_DEBUG(f"This user has reached its limit. Total visits {totalvisits}. Trying other user.")
            # scr_hlp.scr_hlp.handle_logout()
            users.rownum += 1
            if scr_hlp.scr_hlp.useproxy:
                scr_hlp.scr_hlp.initialize_browser_setup()
                raise Exception("No need to continue the caller function.")
            else:
                return users.get_credentials()


        for row in range(sheet.nrows):
            for col in range(sheet.ncols):
                ws.write(row, col, sheet.cell(row, col).value)

        ws.write(users.rownum,2,totalvisits+1)
        ws.write(users.rownum,3,str(datetime.now().date()))
        users.wb.close()
        uname = sheet.cell(users.rownum,0).value
        passw =sheet.cell(users.rownum,1).value
        scr_hlp.scr_hlp.print_if_DEBUG(f"Username = {uname}\t pass = {passw}\t total visits = {totalvisits+1}")
        return uname,passw




