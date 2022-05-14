import requests
from bs4 import BeautifulSoup
import os
import csv
import sys
def zkouska_argumentu(odkaz, vystupni_soubor):

    if odkaz and vystupni_soubor != None:
        if vystupni_soubor.endswith(".csv"):
            return True
        else:
            print("Zadej platné jméno výstupního souboru!")
            return False
    else:
        print("Je potreba zadat dva argumenty!")
        return False

def get_name(soup):
    for tag in soup.find_all('h3'):
        if 'obec:' in tag.text.lower():
            return tag.text.split(': ')[1]

def ziskat_informace_z_webu(odkaz):
    odpoved_serveru = requests.get(odkaz)
    soup = BeautifulSoup(odpoved_serveru.content, 'html.parser')
    tds = soup.find_all('td')
    csv_data = []
    vystupni_data = []

    for td in tds:
        vnitrni_text = td.text
        strings = vnitrni_text.split("\n")
        csv_data.extend([string for string in strings if string])

    del csv_data[2::3]

    odkazy = []

    for mesto in soup.find_all('a'):
        mesto = mesto.get('href')
        odkazy.append(mesto)
        odkazy = list(set(odkazy))

    odkazy_mest = []

    for odkaz_2 in odkazy:
        filtr = "https://volby.cz/pls/ps2017nss/" + odkaz_2
        if filtr[-10:-5] == "vyber":
            odkazy_mest.append(filtr)
    for z in odkazy_mest:
        slovnik = {"kód obce" : None, "název obce" : None,"voliči v seznamu" : None , "vydané obálky" : None, "platné hlasy" : None}
        odpoved_serveru_2 = requests.get(str(z))
        soup_2 = BeautifulSoup(odpoved_serveru_2.content, 'html.parser')
        tds_2 = soup_2.find_all('td')
        obec = str(get_name(soup_2))
        nefiltrovana_data = []
        csv_data_2 = []

        for td in tds_2:
            vnitrni_text_2 = td.text
            nefiltrovana_data.append(vnitrni_text_2)
        csv_data_2.append(nefiltrovana_data[3])
        csv_data_2.append(nefiltrovana_data[4])
        csv_data_2.append(nefiltrovana_data[7])
        strany = []
        hlasy = []

        for x in nefiltrovana_data:
            if any(c.isalpha() for c in x):
                if x != 'X':
                    strany.append(x)
                    index = nefiltrovana_data.index(x) + 1
                    hlasy.append(nefiltrovana_data[index])

        kandidujici_strany = {}
        #for strana in strany:
            #kandidujici_strany[strana] = hlasy.pop(0)
        index_mesta = csv_data.index(obec.strip('\n'))
        slovnik["kód obce"] = csv_data.pop(index_mesta - 1)
        slovnik["název obce"] = csv_data.pop(index_mesta - 1)
        slovnik["voliči v seznamu"] = csv_data_2[0]
        slovnik["vydané obálky"] = csv_data_2[1]
        slovnik["platné hlasy"] = csv_data_2[2]
        for strana in strany:
            slovnik[strana] = hlasy.pop(0)
        vystupni_data.append(slovnik)

    return vystupni_data

def ulozit_jako_csv(data: dict, vystupni_soubor: str) -> None:
    mode = "w" if vystupni_soubor not in os.listdir() else "a"
    with open(vystupni_soubor, mode) as csv_file:
        keys = data[0].keys()
        dict_writer = csv.DictWriter(csv_file, keys)
        dict_writer.writeheader()
        dict_writer.writerows(data)
        csv_file.close()


def election_scraper(odkaz = None, vystupni_soubor = None):
    if zkouska_argumentu(odkaz, vystupni_soubor):
        data = ziskat_informace_z_webu(odkaz)
        ulozit_jako_csv(data, vystupni_soubor)

#election_scraper("https://volby.cz/pls/ps2017nss/ps32?xjazyk=CZ&xkraj=14&xnumnuts=8105", "vysledky_Opava.csv")
if __name__ == "__main__":
    election_scraper(sys.argv[1], sys.argv[2])