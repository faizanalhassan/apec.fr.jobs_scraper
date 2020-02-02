#!/usr/bin/env python3
# coding=UTF-8

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.expected_conditions import presence_of_element_located
from selenium.webdriver.common.action_chains import ActionChains

import urllib.request, os, shutil
from time import sleep

class scr_hlp:
    DEBUG = False
    EXTRADEBUG = False
    d = None
    user_name = ""
    passwrod = ""
    dwnload_dir = ""
    @staticmethod
    def pause_if_EXTRADEBUG(pausing_msg):
        if scr_hlp.EXTRADEBUG:
            input(pausing_msg)
        else:
            scr_hlp.print_if_DEBUG(pausing_msg)
    @staticmethod
    def print_if_DEBUG(log):
        if scr_hlp.DEBUG:
            print(log)
    @staticmethod
    def get_dwnload_dir_path():
        return os.path.join(os.path.dirname(os.path.abspath(__file__)),scr_hlp.dwnload_dir)
    
    @staticmethod
    def get_tmp_dwnld_dir_path():
        return os.path.join(scr_hlp.get_dwnload_dir_path(),"tmp")

    @staticmethod
    def start_chrome():
        options = Options()
#Added from IAO
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        
#End editing
        options.add_argument("--window-size=1920,1080")
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)
        options.add_experimental_option("prefs", {
            "plugins.always_open_pdf_externally": True,
            "download.default_directory": scr_hlp.get_tmp_dwnld_dir_path(),
            "download.prompt_for_download": False,
            "download.directory_upgrade": True,
            "safebrowsing.enabled": True
        })
        params = {'behavior': 'allow', 'downloadPath':scr_hlp.get_tmp_dwnld_dir_path() }
        
        scr_hlp.d = webdriver.Chrome(executable_path="chromedriver",options=options)
        scr_hlp.d.set_page_load_timeout = 60
        
        scr_hlp.d.execute_cdp_cmd('Page.setDownloadBehavior', params)
    @staticmethod
    def close_chrome():
        if(isinstance(scr_hlp.d,webdriver.Chrome)):
            scr_hlp.d.quit()

        scr_hlp.d = None

    @staticmethod
    def is_internet_connected():
            try:
                scr_hlp.print_if_DEBUG("checking connection")
                urllib.request.urlopen('http://google.com')
                scr_hlp.print_if_DEBUG("Connected")
                return True
            except:
                print("Conecction Error")
                return False

    @staticmethod
    def wait_until_connected():
        while True:
            if scr_hlp.is_internet_connected():
                break
            else:
                print("Trying again to connect.")

    @staticmethod
    def load_page(url, do_handle_login = True,wait_ele_xpath = "",ele_count = 1, refresh_also = True):
        scr_hlp.print_if_DEBUG("load_page(\nurl=%s,\ndo_handle_login=%r,\nrefresh_also=%r)"%(url, do_handle_login, refresh_also))
        scr_hlp.wait_until_connected()
        scr_hlp.d.get(url)
        if refresh_also:
            scr_hlp.d.refresh()
        if do_handle_login and scr_hlp.handle_login():
            scr_hlp.load_page(url,False,wait_ele_xpath,ele_count,refresh_also)
        if wait_ele_xpath != "":
            for _ in range(0,10):
                if len(scr_hlp.d.find_elements_by_xpath(wait_ele_xpath)) >= ele_count:
                    break
                sleep(1)



    @staticmethod
    def handle_login():
        login_script = """
            username_node = document.querySelector("#emailid");
            if(username_node.offsetParent === null)
                return false;
            else
            {
                password_node = document.querySelector("#password");
                username_node.value = %s;
                password_node.value = %s;
                document.querySelector("#popin-connexion > div > div:nth-child(2) > div > form > button").click();
                return true;
            }
            """% (scr_hlp.user_name,scr_hlp.passwrod)
        #scr_hlp.print_if_DEBUG("login_script:"+login_script)
        return scr_hlp.d.execute_script(login_script)

    @staticmethod
    def is_next_page_exists():
        next_page_script = """
        nextpage = document.evaluate("//ul[contains(@class,'pagination')]/li/a[contains(text(),'Suiv.')]", document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null ).singleNodeValue;
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
        scr_hlp.print_if_DEBUG("next_page_script result: "+str(result))
        return scr_hlp.d.execute_script(next_page_script)

    @staticmethod
    def handle_download_items(id):
        photo_url = ""
        try:
            if len(scr_hlp.d.find_elements_by_xpath("//*[contains(@id,'photo-profil')]/img[contains(@src,'no-photo.png')]")) == 0:
                photo_url = scr_hlp.d.find_element_by_xpath("//*[contains(@id,'photo-profil')]/img").get_attribute("src")
                scr_hlp.print_if_DEBUG(os.path.join(scr_hlp.get_dwnload_dir_path(),photo_url.split("/")[-1]))
                urllib.request.urlretrieve(photo_url,os.path.join(scr_hlp.get_dwnload_dir_path(),id,photo_url.split("/")[-1]))
        except :
            pass
        scr_hlp.click_element("//button[contains(text(),'Autres actions')]")
        pdf_link = scr_hlp.d.find_element_by_xpath("//button[contains(text(),'Autres actions')]//following-sibling::div/a[contains(text(),'Exporter')]").get_attribute("href")
        params = {'behavior': 'allow', 'downloadPath':os.path.join(scr_hlp.get_dwnload_dir_path(),id) }
        scr_hlp.d.execute_cdp_cmd('Page.setDownloadBehavior', params)
        scr_hlp.d.get(pdf_link)
        #scr_hlp.click_element("//button[contains(text(),'Autres actions')]//following-sibling::div/a[contains(text(),'Exporter')]")
        sleep(1)

        #input("Wait download test")#remove
        return photo_url

    

    @staticmethod
    def add_prefix_to_filename(prefix, time_to_wait=60):
        folder_of_download = scr_hlp.get_tmp_dwnld_dir_path()
        time_counter = 0
        while len(os.listdir(folder_of_download)) == 0:
            pass
        while True:
            try:
                filename = max([f for f in os.listdir(folder_of_download)], key=lambda xa :   os.path.getctime(os.path.join(folder_of_download,xa)))
                break

            except:
                pass
        while '.part' in filename:
            sleep(1)
            time_counter += 1
            if time_counter > time_to_wait:
                #raise Exception('Waited too long for file to download')
                scr_hlp.pause_if_EXTRADEBUG("Waited for file to download for 60 sec. Prefix is not added.")
                return
        filename = max([f for f in os.listdir(folder_of_download)], key=lambda xa :   os.path.getctime(os.path.join(folder_of_download,xa)))
        try:
            shutil.move(os.path.join(folder_of_download, filename), os.path.join(scr_hlp.get_dwnload_dir_path(), prefix+"_"+filename))
            scr_hlp.pause_if_EXTRADEBUG("prefix %s added to download file"%id)
        except:
            scr_hlp.pause_if_EXTRADEBUG("prefix %s couldn't added to download file"%id)
            pass

    @staticmethod
    def get_element_text(xpath,driver=None):
        
        if scr_hlp.is_element_exists(xpath):
            if driver==None:
                driver = scr_hlp.d
                text = scr_hlp.d.execute_script("""node = document.evaluate("%s", document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null ).singleNodeValue;return node != null?node.innerText:'';"""%xpath)
            else:
                text = scr_hlp.d.execute_script("""node = document.evaluate("%s", arguments[0], null, XPathResult.FIRST_ORDERED_NODE_TYPE, null ).singleNodeValue;return node != null?node.innerText:'';"""%xpath,driver)
            return text
            #return driver.find_element_by_xpath(xpath).text
    
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
            scr_hlp.print_if_DEBUG("Clicking %s"%xpath)
            scr_hlp.d.execute_script("""var n = document.evaluate("%s", document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null ).singleNodeValue;n.scrollIntoView();n.click()"""%xpath)
            scr_hlp.print_if_DEBUG("Clicking Complete")
            sleep(1)
            return True
        return False

    @staticmethod
    def get_element_attr(xpath, attr):
        value = ""
        if scr_hlp.is_element_exists(xpath):
            value = scr_hlp.d.execute_script("""return document.evaluate("%s", document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null ).singleNodeValue.getAttribute("%s");"""%(xpath, attr))   
        return value if value != None else ""

