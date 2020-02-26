import psycopg2
from scr_hlp import scr_hlp

pg_db = "candidates"
pg_user = "postgres"
pg_pass = "sheikh123"
pg_host = "127.0.0.1"
pg_port = "5432"


class DB:
    SAVE_ON = True


def replaceq(string):
    return string.replace("'", "''")


def addtoDB(columns_lst, values_lst, dtable):
    if not DB.SAVE_ON:
        return
    conn = psycopg2.connect(user=pg_user,
                            password=pg_pass,
                            host=pg_host,
                            port=pg_port,
                            database=pg_db)

    cur = conn.cursor()
    columns = ", ".join(columns_lst)
    values = ", ".join([f"'{replaceq(v)}'" for v in values_lst])
    insert_q = f"insert into {dtable} ({columns}) values({values});"
    cur.execute(insert_q)
    count = cur.rowcount
    conn.commit()
    scr_hlp.pause_if_EXTRADEBUG(f"{count} Record inserted successfully into mobile table")
    cur.close()
    conn.close()
# v = ['Apec', 'https://www.apec.fr/recruteur/mon-espace/candidapec.html#/detailProfil/2996013?page=0&fonctions=101828&lieux=91&secteursActivite=101753', '2996013', '14/02/2020', '31', '14/02/2020', 'https://www.apec.fr/files/live/mounts/uploads/espaceperso/2996013/photo.jpg.PHOTO_PROFIL2996013.jpg', 'CÉLINE PIGNY', 'En recherche d\'opportunité', '4 ans d\'expérience', 'Recherche opportunité / projet à créer', 'ENTRE 3 ET 6 MOIS', '/telechargement-de-fichier.download.do?from=mesoutils&filename=951616/CV_CA_line_Pigny_-_APEC.pdf.64259981.pdf', '/telechargement-de-fichier.download.do?type=profil&filename=PROFIL_2996013.pdf&id=2996013', 'https://www.linkedin.com/in/céline-pigny-34103665/', '', '', 'Secteur de recherche : l\'Essonne (91) / Paris Envie d\'évoluer vers le développement commercial / gestion de projet. Polyvalente et autonome, je recherche une expérience qui me permettra de relever de nouveaux challenges', 'Chargé d\'affaires, technico-commercial;Commercial;Journalisme, édition;Communication;Commerce international;', '35K€ - 45K€', 'Paris;Essonne;']
# addtoDB(xlsx_hlp.xlsx_hlp.headers_main,v,"main")
