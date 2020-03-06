#!/usr/bin/env python3
# coding=UTF-8

import os
import shutil
import sys
import urllib.request
from time import sleep

from selenium import webdriver
from selenium.webdriver.chrome.options import Options

from usernames import Users, CustomException


class scr_hlp:
    DEBUG = False
    EXTRADEBUG = False
    d = None
    dwnload_dir = ""
    proxies = ['51.158.114.177:8811', '163.172.146.119:8811', '51.158.123.250:8811',
               '163.172.180.18:8811', '51.158.78.107:8811', '51.38.34.40:3128']
    prox_i = 0
    useproxy = True
    list_page_URL = ""

    @staticmethod
    def pause_if_EXTRADEBUG(pausing_msg):
        if scr_hlp.EXTRADEBUG:
            user_input = input(pausing_msg + " (Enter to continue false to turn off pausing...)")
            if user_input.lower() == "false":
                scr_hlp.EXTRADEBUG = False
        else:
            scr_hlp.print_if_DEBUG(pausing_msg)

    @staticmethod
    def print_if_DEBUG(log):
        if scr_hlp.DEBUG:
            print(log)

    @staticmethod
    def get_dwnload_dir_path():
        return os.path.join(os.path.dirname(os.path.abspath(__file__)), scr_hlp.dwnload_dir)

    @staticmethod
    def start_chrome(proxy=""):
        options = Options()

        # Added from IAO
        if not scr_hlp.EXTRADEBUG:
            options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        # End editing
        if proxy != "":
            scr_hlp.print_if_DEBUG(f"using proxy for chrome = {proxy}")
            options.add_argument(f'--proxy-server={proxy}')
        options.add_argument("--window-size=1920,1080")
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)
        options.add_experimental_option("prefs", {
            "plugins.always_open_pdf_externally": True,
            "download.default_directory": scr_hlp.get_dwnload_dir_path(),
            "download.prompt_for_download": False,
            "download.directory_upgrade": True,
            "safebrowsing.enabled": True
        })
        params = {'behavior': 'allow', 'downloadPath': scr_hlp.get_dwnload_dir_path()}

        scr_hlp.d = webdriver.Chrome(options=options)
        scr_hlp.d.set_page_load_timeout = 60

        scr_hlp.d.execute_cdp_cmd('Page.setDownloadBehavior', params)

    @staticmethod
    def close_chrome():
        try:
            scr_hlp.d.quit()
        except:
            pass
        finally:
            scr_hlp.d = None

    @staticmethod
    def initialize_browser_setup():
        scr_hlp.close_chrome()
        proxy = scr_hlp.proxies[scr_hlp.prox_i]
        scr_hlp.print_if_DEBUG(f"Applying proxy = {proxy}") if scr_hlp.useproxy else scr_hlp.print_if_DEBUG("no proxy applied")
        if scr_hlp.useproxy:
            scr_hlp.start_chrome(proxy)
        else:
            scr_hlp.start_chrome()
        scr_hlp.prox_i += 1
        scr_hlp.load_page(scr_hlp.list_page_URL, count_visit=False, do_handle_login=False)
        sleep(2)
        scr_hlp.click_element("//button[@class='optanon-allow-all accept-cookies-button']")

    @staticmethod
    def is_internet_connected():

        try:
            scr_hlp.print_if_DEBUG("checking connection")
            urllib.request.urlopen('http://google.com')
            scr_hlp.print_if_DEBUG("Connected")
            return True
        except:
            print("Connection Error")
            return False

    @staticmethod
    def wait_until_connected():
        while True:
            if scr_hlp.is_internet_connected():
                break
            else:
                print("Trying again to connect.")

    @staticmethod
    def load_page(url, count_visit, do_handle_login=True, wait_ele_xpath="", ele_count=1, refresh_also=True):
        scr_hlp.print_if_DEBUG(f"load_page(url={url}, do_handle_login={do_handle_login},"
                               f" wait_ele_xpath={wait_ele_xpath}, ele_count={ele_count},"
                               f" refresh_also={refresh_also}, count_visit={count_visit})")
        scr_hlp.wait_until_connected()
        scr_hlp.print_if_DEBUG("loading start")
        scr_hlp.d.get(url)
        scr_hlp.print_if_DEBUG("loading complete")
        if refresh_also:
            scr_hlp.d.refresh()

        if do_handle_login:
            try:
                username, password = Users.get_credentials(count_visit)
                # scr_hlp.pause_if_EXTRADEBUG("Login check")
                while scr_hlp.handle_login(username, password):
                    # scr_hlp.pause_if_EXTRADEBUG("Tried to login")
                    sleep(3)
                    if scr_hlp.is_element_exists("//*[contains(text(),"
                                                 "'Votre identifiant ou votre mot de passe est incorrect.')"
                                                 " and not(contains(@class,'alert-d-none'))]"):
                        command = input(f"Webpage is saying that your credentials are wrong.\n"
                                        f"Recheck the credentials username={username}, password={password}"
                                        f" listed in row num {Users.row_num} and enter y to continue: ")
                        if command.lower() != 'y':
                            scr_hlp.d.quit()
                            sys.exit()
                        else:
                            scr_hlp.d.refresh()
                            username, password = Users.get_credentials(count_visit)
                    else:
                        scr_hlp.print_if_DEBUG("Login success")
                        break
            except CustomException as ce:
                scr_hlp.print_if_DEBUG("\t\tMy Custom Exception: Browser reopened " + str(ce))
                scr_hlp.load_page(url=url, count_visit=count_visit, do_handle_login=do_handle_login,
                                  wait_ele_xpath=wait_ele_xpath, ele_count=ele_count, refresh_also=refresh_also)
                return

        if wait_ele_xpath != "":
            for i in range(0, 30):
                pass
                scr_hlp.print_if_DEBUG(f"Waiting for {wait_ele_xpath}, iteration = {i}")
                if len(scr_hlp.d.find_elements_by_xpath(wait_ele_xpath)) >= ele_count:
                    scr_hlp.print_if_DEBUG(f"Elements found")
                    break

                elif i == 11:
                    ans = input("Waited too long but page is not loading its dynamic contents."
                                " Do you want to try load again? (y)")
                    if ans.lower() == 'y':
                        scr_hlp.load_page(url=url, count_visit=count_visit, do_handle_login=do_handle_login,
                                          wait_ele_xpath=wait_ele_xpath, ele_count=ele_count, refresh_also=refresh_also)
                elif i % 3 == 0:
                    if len(scr_hlp.d.find_elements_by_xpath(wait_ele_xpath)) != 0:
                        break
                    scr_hlp.print_if_DEBUG(f"Refreshing browser. Because {wait_ele_xpath} not found.")
                    scr_hlp.d.refresh()
                sleep(5)

    @staticmethod
    def handle_login(username, password):
        while True:
            if len(scr_hlp.d.find_elements_by_xpath("//input[@id='emailid']")) >= 1:
                break
            sleep(1)
        login_script = f"""
            username_node = document.querySelector("#emailid");
            if(username_node.offsetParent === null)
                return false;
            else
            {{
                password_node = document.querySelector("#password");
                username_node.value = '{username}';
                password_node.value = '{password}';
                document.querySelector("#popin-connexion > div > div:nth-child(2) > div > form > button").click();
                return true;
            }}
            """
        scr_hlp.print_if_DEBUG("login with:" + login_script)
        return scr_hlp.d.execute_script(login_script)

    @staticmethod
    def is_next_page_exists():
        next_page_script = """
        nextpage = document.evaluate("//ul[contains(@class,'pagination')]/li/a[contains(text(),'Suiv.')]",
         document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null ).singleNodeValue;
        if(nextpage)
        {
           return true;
        }
        else
        {
           return false;
        }
        """
        result = scr_hlp.d.execute_script(next_page_script)
        scr_hlp.print_if_DEBUG("next_page_script result: " + str(result))
        return scr_hlp.d.execute_script(next_page_script)

    @staticmethod
    def handle_download_items(profile_id):
        photo_url = ""

        scr_hlp.click_element("//button[contains(text(),'Autres actions')]")
        pdf_link = scr_hlp.d.find_element_by_xpath("//button[contains(text(),'Autres actions')]//following-sibling"
                                                   "::div/a[contains(text(),'Exporter')]").get_attribute("href")
        params = {'behavior': 'allow', 'downloadPath': os.path.join(scr_hlp.get_dwnload_dir_path(), profile_id)}
        scr_hlp.d.execute_cdp_cmd('Page.setDownloadBehavior', params)
        current_page = scr_hlp.d.current_url
        scr_hlp.load_page(pdf_link, count_visit=False, refresh_also=False)
        # scr_hlp.load_page(current_page, count_visit=False, wait_ele_xpath="//*[contains(@id,'photo-profil')]/img")
        try:
            if len(scr_hlp.d.find_elements_by_xpath("//*[contains(@id,'photo-profil')]"
                                                    "/img[contains(@src,'no-photo.png')]")) == 0:
                photo_url = scr_hlp.d.find_element_by_xpath("//*[contains(@id,'photo-profil')]/img") \
                    .get_attribute("src")
                photo_filename = os.path.join(scr_hlp.get_dwnload_dir_path(), profile_id, photo_url.split("/")[-1])
                scr_hlp.print_if_DEBUG(photo_filename)
                urllib.request.urlretrieve(photo_url, photo_filename)
        except:
            pass
        # input("Wait download test")#remove
        return photo_url

    @staticmethod
    def add_prefix_to_filename(prefix, time_to_wait=60):
        folder_of_download = scr_hlp.get_dwnload_dir_path()
        time_counter = 0
        while len(os.listdir(folder_of_download)) == 0:
            pass
        while True:
            try:
                filename = max(
                    [f for f in os.listdir(folder_of_download)],
                    key=lambda xa: os.path.getctime(os.path.join(folder_of_download, xa)))
                break

            except:
                pass
        while '.part' in filename:
            sleep(1)
            time_counter += 1
            if time_counter > time_to_wait:
                # raise Exception('Waited too long for file to download')
                scr_hlp.pause_if_EXTRADEBUG("Waited for file to download for 60 sec. Prefix is not added.")
                return
        filename = max([f for f in os.listdir(folder_of_download)],
                       key=lambda xa: os.path.getctime(os.path.join(folder_of_download, xa)))
        try:
            shutil.move(os.path.join(folder_of_download, filename),
                        os.path.join(scr_hlp.get_dwnload_dir_path(), prefix + "_" + filename))
            scr_hlp.pause_if_EXTRADEBUG("prefix %s added to download file" % id)
        except:
            scr_hlp.pause_if_EXTRADEBUG("prefix %s couldn't added to download file" % id)
            pass

    @staticmethod
    def get_element_text(xpath, driver=None):

        # if scr_hlp.is_element_exists(xpath):
        if driver is None:
            text = scr_hlp.d.execute_script(
                """node = document.evaluate("%s", document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null ).singleNodeValue;return node != null?node.innerText:'';""" % xpath)
        else:
            text = scr_hlp.d.execute_script(
                """node = document.evaluate("%s", arguments[0], null, XPathResult.FIRST_ORDERED_NODE_TYPE, null ).singleNodeValue;return node != null?node.innerText:'';""" % xpath,
                driver)
        return text.strip()
        # return driver.find_element_by_xpath(xpath).text

    @staticmethod
    def get_element(xpath):
        if scr_hlp.is_element_exists(xpath):
            return scr_hlp.d.find_element_by_xpath(xpath)
        else:
            return None

    @staticmethod
    def is_element_exists(xpath):
        try:
            scr_hlp.d.find_element_by_xpath(xpath)
            return True
        except:
            return False

    @staticmethod
    def click_element(xpath):
        if scr_hlp.is_element_exists(xpath):
            scr_hlp.print_if_DEBUG("Clicking %s" % xpath)
            scr_hlp.d.execute_script(
                """var n = document.evaluate("%s", document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null ).singleNodeValue;n.scrollIntoView();n.click()""" % xpath)
            scr_hlp.print_if_DEBUG("Clicking Complete")
            sleep(1)
            return True
        return False

    @staticmethod
    def get_element_attr(xpath, attr):
        value = ""
        if scr_hlp.is_element_exists(xpath):
            value = scr_hlp.d.execute_script(
                """return document.evaluate("%s", document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null ).singleNodeValue.getAttribute("%s");""" % (xpath, attr))
        return value if value is not None else ""
