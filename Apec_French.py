#!/usr/bin/env python3
# coding=UTF-8

from scr_hlp import scr_hlp, sleep, os
from xlsx_hlp import xlsx_hlp
from datetime import datetime

scr_hlp.DEBUG = True
scr_hlp.EXTRADEBUG = True #use for pausing on some places

scr_hlp.dwnload_dir = "downloads"
scr_hlp.user_name = "'100158267W'"
scr_hlp.passwrod = "'Bestshore*05'"

xlsx_hlp.folder_name = "files_"+datetime.now().strftime("%d%m%y")
xlsx_hlp.filename = "extapec_"+datetime.now().strftime("%d%m%y")

#Filters
Fonctions= ['&fonctions=101828', '&fonctions=101829', '&fonctions=101830',]
lieux= ['&lieux=91', '&lieux=77', '&lieux=75',]
secteursActivite= ['&secteursActivite=101753', '&secteursActivite=101755','&secteursActivite=101757',]

list_page_URL = "https://www.apec.fr/recruteur/mon-espace/candidapec.html#/rechercheNormale?page=%s"

if not os.path.isdir(scr_hlp.get_dwnload_dir_path()):
    os.mkdir(scr_hlp.get_dwnload_dir_path())
    scr_hlp.pause_if_EXTRADEBUG("Download dir created")


if not os.path.isdir(scr_hlp.get_tmp_dwnld_dir_path()):
    os.mkdir(scr_hlp.get_tmp_dwnld_dir_path())
    scr_hlp.pause_if_EXTRADEBUG("tmp dir created")

for fonc in Fonctions:
    for loc in lieux:
        for sec in secteursActivite:
            page_num = 0
            list_page_URL = list_page_URL + fonc + loc + sec
            xlsx_hlp.create_wb(fonc + loc + sec)
            scr_hlp.start_chrome()
            scr_hlp.load_page(list_page_URL)
            sleep(2)
            scr_hlp.click_element("//button[@class='optanon-allow-all accept-cookies-button']")
            
            while True:
                scr_hlp.load_page(list_page_URL%page_num, wait_ele_xpath="//a[@class='actualLink' and contains(@href,'/detailProfil/')]", ele_count=20)
                candidates_nodes = scr_hlp.d.find_elements_by_xpath("//a[@class='actualLink' and contains(@href,'/detailProfil/')]")
                scr_hlp.print_if_DEBUG("Total candidates on this page are: "+str(len(candidates_nodes)))
                is_next_exists = scr_hlp.is_next_page_exists()
                scr_hlp.print_if_DEBUG("is_next_exists = %r"%scr_hlp.is_next_page_exists())
                c_page_URLs = []
                #save all urls in current page
                for i in range(0,len(candidates_nodes)):
                    c_URL = candidates_nodes[i].get_attribute("href")
                    scr_hlp.print_if_DEBUG(str(i)+": Candidate link: "+c_URL)
                    c_page_URLs.append(c_URL)

                #load those urls
                for j in range(0,len(c_page_URLs)):
                    
                    scr_hlp.load_page(c_page_URLs[j], wait_ele_xpath="//*[contains(@id,'photo-profil')]/img", ele_count=1)
                    
                    scr_hlp.click_element("//*[contains(@class,'condonnee-profil')]/button") # button hiding tel and mail
                    id = c_page_URLs[j].split("/")[-1].split("?")[0]
                    photo_url = scr_hlp.handle_download_items(id)
                    row_main = []
                    row_main.append(c_page_URLs[j].split("/")[-1].split("?")[0]) #id
                    row_main.append(scr_hlp.get_element_text("//*[contains(text(),'Mis à jour le')]")) #date_maj
                    row_main.append(scr_hlp.get_element_text("//*[contains(text(),'Profil consulté')]")) #nb_consult
                    row_main.append(scr_hlp.get_element_text("//*[contains(text(),'Dernière consultation')]")) #date_der
                    row_main.append(photo_url) #photo_url
                    row_main.append(scr_hlp.get_element_text("//*[@id='name']")) #name
                    row_main.append(scr_hlp.get_element_text("//*[@id='poste']")) #poste
                    row_main.append(scr_hlp.get_element_text("//*[@id='experience']")) #exp
                    row_main.append(scr_hlp.get_element_text("//*[@id='title']")) #title
                    row_main.append(scr_hlp.get_element_text("//*[@id='dispo']")) #dispo
                    row_main.append(scr_hlp.get_element_attr("//*[contains(@class,'cv-profil')]/a[contains(@href,'filename')]","href")) #file url
                    row_main.append(scr_hlp.get_element_attr("//*[contains(@id,'linkedin-icon')]/parent::a","href")) #linkedin url
                    row_main.append(scr_hlp.get_element_text("//*[contains(@class,'cv-contact-profil')]//a[contains(@href,'tel:')]")) #tell
                    row_main.append(scr_hlp.get_element_text("//*[contains(@class,'cv-contact-profil')]//a[contains(@href,'mailto:')]")) #mail
                    row_main.append(scr_hlp.get_element_text("//*[contains(text(),'Objectif et Souhaits professionnels')]/following-sibling::*")) #obj
                    row_main.append(scr_hlp.d.execute_script("""var fonc = document.evaluate("//*[contains(text(),'Fonctions :')]/parent::*/following-sibling::*", document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null ).singleNodeValue.children;str = "";for( i = 0;i<fonc.length;i++){str += fonc[i].innerText +";";}return str;""")) #fonc
                    row_main.append(scr_hlp.get_element_text("//*[contains(text(),'Salaire souhaité :')]/parent::*/following-sibling::*")) #sal
                    row_main.append(scr_hlp.d.execute_script("""var nodes = document.evaluate("//*[contains(text(),'Lieux :')]/parent::*/following-sibling::*", document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null ).singleNodeValue.children;str = "";for( i = 0;i<nodes.length;i++){str += nodes[i].innerText +";";}return str;""")) #Lieux 
                    scr_hlp.print_if_DEBUG(row_main)

                    for k in range(0,len(row_main)):
                        xlsx_hlp.ws_main.write(xlsx_hlp.row_num_main,k,row_main[k])
                    xlsx_hlp.row_num_main += 1

                    scr_hlp.click_element("//section[contains(@class,'section-competences')]/*[contains(text(),'Voir les autres compétences (1)')]")
                    comp_eles = scr_hlp.d.find_elements_by_xpath("//*[@class='competence-name' and ./parent::div/following-sibling::div[@class='col-md-8']]/parent::div/parent::div")
                    for e in comp_eles:
                        stars_eles = e.find_elements_by_xpath(".//*[@class='competence-name']/following-sibling::div[contains(@class,'stars')]/*")
                        total_stars = 0
                        for se in stars_eles:
                            if("xstar-yellow.png" in se.value_of_css_property("background-image")):
                                total_stars += 1
                        row_comp = []
                        row_comp.append(id)
                        row_comp.append(e.find_element_by_xpath(".//*[@class='competence-name']").text) #comp 
                        row_comp.append(str(total_stars))#total stars
                        row_comp.append(e.find_element_by_xpath(".//*[@class='competence-level']").text) #comp level
                        row_comp.append(e.find_element_by_xpath(".//*[@class='competence-name']/parent::div/following-sibling::div").text)# comp desc
                        scr_hlp.print_if_DEBUG("row_comp: "+str(row_comp))
                        for l in range(0, len(row_comp)):
                            xlsx_hlp.ws_comp.write(xlsx_hlp.row_num_comp,l,row_comp[l])
                        xlsx_hlp.row_num_comp += 1

                    lang_eles = scr_hlp.d.find_elements_by_xpath("//*[@class='competence-name' and not(./parent::div/following-sibling::div[@class='col-md-8'])]/parent::div")
                    for e in lang_eles:
                        stars_eles = e.find_elements_by_xpath(".//*[@class='competence-name']/following-sibling::div[contains(@class,'stars')]/*")
                        total_stars = 0
                        for se in stars_eles:
                            if("xstar-yellow.png" in se.value_of_css_property("background-image")):
                                total_stars += 1
                        row_lang = []
                        row_lang.append(id)
                        row_lang.append(e.find_element_by_xpath(".//*[@class='competence-name']").text) #lang 
                        row_lang.append(str(total_stars)) #total stars
                        row_lang.append(e.find_element_by_xpath(".//*[@class='competence-level']").text) #lang level
                        scr_hlp.print_if_DEBUG("row_lang: "+str(row_lang))
                        for l in range(0, len(row_lang)):
                            xlsx_hlp.ws_lang.write(xlsx_hlp.row_num_lang,l,row_lang[l])
                        xlsx_hlp.row_num_lang += 1
        

                    for e in scr_hlp.d.find_elements_by_xpath("//*[contains(@class,'list-atouts')]"):
                        row_atouts = []
                        row_atouts.append(id)
                        row_atouts.append(e.text)
                        scr_hlp.print_if_DEBUG("row_atouts: "+str(row_atouts))
                        for l in range(0, len(row_atouts)):
                            xlsx_hlp.ws_atouts.write(xlsx_hlp.row_num_atouts,l,row_atouts[l])
                        xlsx_hlp.row_num_atouts += 1

                    count = 0
                    for e in scr_hlp.d.find_elements_by_xpath("//section[contains(@class,'section-moments')]//ngu-tile"):
                        if(count > 0 and count%3 == 0):
                            scr_hlp.click_element("//button[@class='slick-next hidden-xs']")
                        count += 1
                        dd_df = e.find_element_by_xpath(".//h4[contains(@class,'date')]").text.split("à")
                        row_nb_mom = []
                        row_nb_mom.append(id)
                        row_nb_mom.append(dd_df[0]) #dd
                        if len(dd_df) > 1:
                            row_nb_mom.append(dd_df[1]) #df
                        else:
                            row_nb_mom.append('') #df
                        row_nb_mom.append(scr_hlp.get_element_text(".//p[contains(@class,'moment-upper')]", e)) #type
                        row_nb_mom.append(scr_hlp.get_element_text(".//h3[contains(@class,'job')]", e)) #title
                        row_nb_mom.append(scr_hlp.get_element_text(".//h5[contains(@class,'domaine')]", e)) #tagline
                        row_nb_mom.append(scr_hlp.get_element_text(".//div[contains(@class,'companyName')]/span", e)) #comp
                        row_nb_mom.append(scr_hlp.get_element_text(".//span[./parent::div[contains(@class,'lieux')] or contains(@class,'school-type')]", e)) #location
                        row_nb_mom.append(scr_hlp.get_element_text(".//span[contains(@class,'domaine-entp')]", e)) #desc
                        scr_hlp.print_if_DEBUG("row_nb_mom: "+str(row_nb_mom))
                        for l in range(0, len(row_nb_mom)):
                            xlsx_hlp.ws_nb_moments.write(xlsx_hlp.row_num_nb_moments,l,row_nb_mom[l])
                        xlsx_hlp.row_num_nb_moments += 1
                 
                xlsx_hlp.save_wb()#saves after a page
                scr_hlp.pause_if_EXTRADEBUG("Going to add page")
                if not is_next_exists:
                    break
                scr_hlp.pause_if_EXTRADEBUG("page added")
                page_num += 1
            xlsx_hlp.wb.close()
            scr_hlp.close_chrome()