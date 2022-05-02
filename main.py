import requests
from bs4 import BeautifulSoup
import os
import csv
from pprint import pprint
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
            #print(tag.text.lower())
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
        #mesto_2 = mesto.findChildren()
        #odkazy.append(mesto_2.get('href'))
        #mesto_2= str(mesto.contents)
        odkazy.append(mesto)
        odkazy = list(set(odkazy))
    ##pprint(odkazy)
        #odkazy.append(mesto[10:71].strip("\">X</a>]"))

    odkazy_mest = []

    for odkaz_2 in odkazy:
        filtr = "https://volby.cz/pls/ps2017nss/" + odkaz_2
        if filtr[-10:-5] == "vyber":
            odkazy_mest.append(filtr)
    #print(odkazy_mest)
    for z in odkazy_mest:
        #print(z)
        slovnik = {"kód obce" : None, "název obce" : None,"voliči v seznamu" : None , "vydané obálky" : None, "platné hlasy" : None, "kandidujici strany" : None}
        odpoved_serveru_2 = requests.get(str(z))
        soup_2 = BeautifulSoup(odpoved_serveru_2.content, 'html.parser')
        tds_2 = soup_2.find_all('td')
        obec = str(get_name(soup_2))
        #print(obec)
        #obec = [tag.text.split(' ')[1] for tag in soup.find_all('h3') if 'obec:' in tag.text.lower()][0]
        #h3 = soup_2.find_all('h3')
        #obec = h3[2].get('Obec')
        #obec.strip("<h3>")
        #div = soup_2.find_all("div")
        #mesto = div.get('Obec')
        #print("---------------------------------------------")
        #print(obec)
        #print("---------------------------------------------")
        nefiltrovana_data = []
        csv_data_2 = []

        for td in tds_2:
            #print(td)
            vnitrni_text_2 = td.text
            #print(vnitrni_text_2)
            nefiltrovana_data.append(vnitrni_text_2)
        csv_data_2.append(nefiltrovana_data[3])
        csv_data_2.append(nefiltrovana_data[4])
        csv_data_2.append(nefiltrovana_data[7])
        strany = []
        hlasy = []
        #print(nefiltrovana_data)
        #print(nefiltrovana_data[11::5])
        for x in nefiltrovana_data:
            if any(c.isalpha() for c in x):
                if x != 'X':
                    strany.append(x)
                    index = nefiltrovana_data.index(x) + 1
                    hlasy.append(nefiltrovana_data[index])
        #print(hlasy)
        #try:
        kandidujici_strany = {}
        for strana in strany:
            kandidujici_strany[strana] = hlasy.pop(0)
        #print(csv_data)
        index_mesta = csv_data.index(obec.strip('\n'))
        #print(index_mesta)
        slovnik["kód obce"] = csv_data.pop(index_mesta - 1)
        slovnik["název obce"] = csv_data.pop(index_mesta - 1)
        slovnik["voliči v seznamu"] = csv_data_2[0]
        slovnik["vydané obálky"] = csv_data_2[1]
        slovnik["platné hlasy"] = csv_data_2[2]
        slovnik["kandidujici strany"] = kandidujici_strany
        vystupni_data.append(slovnik)
        #except IndexError:
            #print("oops")
    return vystupni_data
    #print(csv_data_2)
        #table = soup_2.find('table')
        #table = soup_2.findChildren('table')[0]
        #rows = table.findChildren('tr')
        #for row in rows:
            #cells = row.findChildren('td')
        #for cell in cells:
            #cell_content = cell.getText()
            #print(cell)
        #tds_2 = str([ele.text.strip() for ele in tds_2])
        #tds_2.split(",")
        #tds_2_1 = []
        #for tds in tds_2:
            #if tds.isalpha():
                #tds_2_1.append(tds)
        #print(tds_2)
        #inner_text = tds_2[0].text
        #strings = inner_text.split("\n")
        #csv_data_2.extend([string for string in strings if string])
        #for td in tds_2:
            #inner_text = td.text
            #strings = inner_text.split("\n")

            #csv_data_2.extend([string for string in strings if string])
        #pprint(csv_data_2)
        #print(odpoved_serveru_2.text)


    #pprint(soup.find_all("a"))
    #print(str(soup.find_all("a")))
    #for x in soup.find_all("a"):
        #print(x)

def ulozit_jako_csv(data: dict, vystupni_soubor: str) -> None:
    #poprve = True
    mode = "w" if vystupni_soubor not in os.listdir() else "a"
    with open(vystupni_soubor, mode) as csv_file:
        keys = data[0].keys()
        #a_file = open("output.csv", "w")
        dict_writer = csv.DictWriter(csv_file, keys)
        dict_writer.writeheader()
        dict_writer.writerows(data)
        csv_file.close()
        #for x in data:
            #if poprve == True:
            #header = x.keys()
            #reader = csv.DictReader(csv_file)
            #writer = csv.DictWriter(csv_file, fieldnames=header)
                #poprve = False
            #else:
            #reader = csv.DictReader(csv_file)
            #writer = csv.DictWriter(csv_file, fieldnames=header)
            #if mode == "w":
                #writer.writeheader()
            #writer.writerow(x)

def election_scraper(odkaz = None, vystupni_soubor = None):
    if zkouska_argumentu(odkaz, vystupni_soubor):
        data = ziskat_informace_z_webu(odkaz)
        ulozit_jako_csv(data, vystupni_soubor)

#election_scraper("https://volby.cz/pls/ps2017nss/ps32?xjazyk=CZ&xkraj=12&xnumnuts=7101", "vysledky_Jesenik.csv")
#main("","")
#election_scraper('https://volby.cz/pls/ps2017nss/ps32?xjazyk=CZ&xkraj=12&xnumnuts=7103', 'vyslekdy_prostejov.csv')
#election_scraper('https://volby.cz/pls/ps2017nss/ps32?xjazyk=CZ&xkraj=12&xnumnuts=7103', 'vysledky_prostejov.csv')
# 'https://volby.cz/pls/ps2017nss/ps32?xjazyk=CZ&xkraj=12&xnumnuts=7103', 'vysledky_prostejov.csv'
election_scraper("https://volby.cz/pls/ps2017nss/ps32?xjazyk=CZ&xkraj=6&xnumnuts=4201", "vysledky_Decin.csv")
