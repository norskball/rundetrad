import datetime
import os
from os import path

flair = {
"Default": "[](/flair-tom)",
"Aalesund": "[](/flair-aalesund)Aalesund",
"Ã…sane": "[](/flair-aasane)Ã…sane",
"BodÃ¸/Glimt": "[](/flair-bodoe-glimt)BodÃ¸/Glimt",
"Brann": "[](/flair-brann)Brann",
"Bryne": "[](/flair-bryne)Bryne",
"Fredrikstad": "[](/flair-fredrikstad)Fredrikstad",
"HamKam": "[](/flair-hamkam)HamKam",
"Haugesund": "[](/flair-haugesund)Haugesund",
"Jerv": "[](/flair-jerv)Jerv",
"KFUM": "[](/flair-kfum-oslo)KFUM",
"Kongsvinger": "[](/flair-kongsvinger)Kongsvinger",
"Kristiansund BK": "[](/flair-kristiansund-bk)Kristiansund",
"LillestrÃ¸m": "[](/flair-lillestroem)LillestrÃ¸m",
"Lyn": "[](/flair-lyn)Lyn",
"MjÃ¸ndalen": "[](/flair-mjoendalen)MjÃ¸ndalen",
"Molde": "[](/flair-molde)Molde",
"Moss": "[](/flair-moss)Moss",
"Odd": "[](/flair-odd)Odd",
"Ranheim": "[](/flair-ranheim-tf)Ranheim",
"Raufoss": "[](/flair-raufoss)Raufoss",
"Rosenborg": "[](/flair-rosenborg)Rosenborg",
"Sandefjord": "[](/flair-sandefjord)Sandefjord",
"Sandnes Ulf": "[](/flair-sandnes-ulf)Sandnes Ulf",
"Sarpsborg 08": "[](/flair-sarpsborg-08)Sarpsborg 08",
"Sogndal": "[](/flair-sogndal)Sogndal",
"StabÃ¦k": "[](/flair-stabaek)StabÃ¦k",
"Start": "[](/flair-start)Start",
"StrÃ¸mmen": "[](/flair-stroemmen)StrÃ¸mmen",
"StrÃ¸msgodset": "[](/flair-stroemsgodset)StrÃ¸msgodset",
"TromsÃ¸": "[](/flair-tromsoe)TromsÃ¸",
"Ull/Kisa": "[](/flair-ullensaker-kisa)Ull/Kisa",
"VÃ¥lerenga": "[](/flair-vaalerenga)VÃ¥lerenga",
"Viking": "[](/flair-viking)Viking",
}

def lag_liste(eliteserien):
    if eliteserien:
        file = open("rundetråd - eliteserien.csv", "r")
        tabell = []
        for line in file:
            line_replace = line.replace(",,", "")
            line_strip = line_replace.strip()
            lag = line_strip.split(",")
            tabell.append(lag)
        file.close()
    else:
        file = open("rundetråd - 1. divisjon.csv", "r")
        tabell = []
        for line in file:
            line_replace = line.replace(",,", "")
            line_strip = line_replace.strip()
            lag = line_strip.split(",")
            tabell.append(lag)
        file.close()
    return tabell

def list_ligatabell(list, antall):
    i = 0
    tabell = []
    for streng in list:
        substring = "Tabell"
        if substring in streng:
            k = 1
            while k <= antall:
                tabell.append(list[k+1])
                k += 1
        i += 1
    for lag in tabell:
        for element in lag:
            if element == "":
                lag.pop(lag.index(element))
    tabell = formater_tabell(tabell)
    return tabell

def list_terminliste(list):
    liste_ut = []
    substring = "element.do"
    for streng in list:
        for element in streng:
            if substring in element:
                liste_ut.append(streng)
            else:
                pass
    liste_ut = formater_terminliste(liste_ut)
    return liste_ut


def list_toppscorer(list, antall):
    substring = "Toppscorer"
    liste_scorer = []
    index = index_2d(list, substring)
    for spiller in list[index[0]+2:index[0]+5]:
        liste_scorer.append(spiller)
        if spiller[2] in flair:
            spiller[2] = flair.get(spiller[2])
        else:
            spiller[2] = flair.get("Default")+spiller[2]
    return liste_scorer


def index_2d(myList, v):
    for i, x in enumerate(myList):
        if v in x:
            return i, x.index(v)

def list_assist(list, antall):
    substring = "Assistkonge"
    assistListe = []
    index = index_2d(list, substring)
    for spiller in list[index[0] + 2:index[0] + 5]:
        assistListe.append(spiller)
        if spiller[2] in flair:
            spiller[2] = flair.get(spiller[2])
        else:
            spiller[2] = flair.get("Default") + spiller[2]
    return assistListe

def list_runde(liste, nummer, hoved):
    runde_liste = []
    if hoved == True:
        i = 0
        dageni_dag = datetime.datetime.now()
        for kamp in liste:
            dagNummer = datetime.datetime(int(kamp[i][6:10]), int(kamp[i][3:5]), int(kamp[i][0:2]))
            dagNummer = dagNummer.strftime("%j")
            #inkluderer neste hovedrunde
            if int(dagNummer) - int(dageni_dag.strftime("%j")) in range(-2, 7, 1) and int(kamp[1]) == int(nummer):
                runde_liste.append(kamp)
        i =+ 1

    if hoved == False:
        i = 0
        dageni_dag = datetime.datetime.now()
        for kamp in liste:
            dagNummer = datetime.datetime(int(kamp[i][6:10]), int(kamp[i][3:5]), int(kamp[i][0:2]))
            dagNummer = dagNummer.strftime("%j")
            #inkluderer kamper den neste uken++ som ikke tilhører inneværende eller neste runde.
            if int(dagNummer) - int(dageni_dag.strftime("%j")) in range(0, 10, 1) and int(kamp[1]) != int(nummer) and int(kamp[1]) != int(nummer)+1:
                runde_liste.append(kamp)
        i =+ 1
    return runde_liste

def formater_tabell(liste):
    for lag in liste:
        if lag[1] in flair:
            lag[1] = flair.get(lag[1])
        else:
            lag[1] = flair.get("Default")+lag[1]
    return liste

def formater_terminliste(liste):
    dato_minne = 0
    for kamp in liste:

        # Legger til manglende datoer
        if len(kamp[0]) != 0:
            dato_minne = kamp[0]
        else:
            # kamp.insert(0, dato_minne)
            kamp[0] = dato_minne

        # Formaterer rundenummer
        if ". runde" in kamp[1]:
            kamp[1] = kamp[1].replace(". runde", "")

        if kamp[2] in flair:
            kamp[2] = flair.get(kamp[2])
        else:
            kamp[2] = flair.get("Default")+kamp[2]

        kamp[3] = "[" + kamp[3] + "]"

        kamp[4] = "(http://altomfotball.no/altomfotball.no" + kamp[4] + ")"
        kamp[3] = kamp[3] + kamp[4]

        if kamp[5] in flair:
            kamp[5] = flair.get(kamp[5])
        else:
            kamp[5] = flair.get("Default")+kamp[5]

        kamp[4] = kamp[5]

        kamp[5] = kamp[6]
        kamp.remove(kamp[6])
        if "\n" in kamp[5]:
            kamp[5] = kamp[5].replace("\n", "")
    return liste


def sjekke_hovedrunde (list):
    i = 0
    runde = []
    dageni_dag = datetime.datetime.now()
    for kamp in list:
        dag_nummer = datetime.datetime(int(kamp[i][6:10]), int(kamp[i][3:5]), int(kamp[i][0:2]))
        dag_nummer = dag_nummer.strftime("%j")
        if int(dag_nummer) - int(dageni_dag.strftime("%j")) in range(-2, 7, 1):
            runde.append(kamp[1])
    return most_common(runde)

def skriv_ut (tabell, runde, ekstra, maal, assist, eliteserien):

    #Tabell
    if eliteserien :
        slutt_fil = open("eliteserien-ferdig.txt", "a")
        slutt_fil.write("# Tabell fÃ¸r runden\n######[](http://reddit.com#)\n"+
               "Nr | Lag | K | S | U | T | + | - | + / - | P |\n"+
               "--- | --- | ---- | ----: | ----: | ----: | ----: | ----: | ----: | ----: |\n")
    else :
        slutt_fil = open("obos-ferdig.txt", "a")
        slutt_fil.write("# Tabell fÃ¸r runden\n#####[](http://reddit.com#)\n" +
                   "Nr | Lag | K | S | U | T | + | - | + / - | P |\n" +
                   "--- | --- | ---- | ----: | ----: | ----: | ----: | ----: | ----: | ----: |\n")

    for lag in tabell:
        for element in lag:
            slutt_fil.write(str(element)+"|")
        slutt_fil.write("\n")
    slutt_fil.close()

    #Rundens kamper
    if eliteserien :
        slutt_fil = open("eliteserien-ferdig.txt", "a")
    else:
        slutt_fil = open("obos-ferdig.txt", "a")
    slutt_fil.write("#Rundens kamper\nDato|Hjemmelag||Bortelag|Kanal\n---|----|:----:|----|----\n")
    for kamp in runde:
        i = 0
        for element in kamp:
            if i == 1:
                i += 1
            else:
                slutt_fil.write(str(element)+"|")
                i += 1
        slutt_fil.write("\n")
    slutt_fil.close()

    #Omberammede kamper
    if ekstra:
        if eliteserien :
            slutt_fil = open("eliteserien-ferdig.txt", "a")
        else :
            slutt_fil = open("obos-ferdig.txt", "a")
        slutt_fil.write("#Omberammede kamper\nDato|Runde|Hjemmelag||Bortelag|Kanal\n" +
        "---|:----:|----|:----:|----|----\n")
        slutt_fil.close()
    else:
        pass

    if eliteserien :
        slutt_fil = open("eliteserien-ferdig.txt", "a")
    else :
        slutt_fil = open("obos-ferdig.txt", "a")

    for kamp in ekstra:
        for element in kamp:
            slutt_fil.write(str(element)+"|")
        slutt_fil.write("\n")
    slutt_fil.close()

    #Toppscorer
    if eliteserien :
        slutt_fil = open("eliteserien-ferdig.txt", "a")
    else :
        slutt_fil = open("obos-ferdig.txt", "a")
    slutt_fil.write("#Toppscorer\nNr | Spiller | Lag | M | K | \n---|:--|:--|--|--|--\n")
    for spiller in maal:
        for element in spiller:
                slutt_fil.write(str(element)+"|")
        slutt_fil.write("\n")
    slutt_fil.close()

    #Assist
    if eliteserien :
        slutt_fil = open("eliteserien-ferdig.txt", "a")
    else :
        slutt_fil = open("obos-ferdig.txt", "a")
    slutt_fil.write("#Assist\nNr | Spiller | Lag | A | K | \n---|:--|:--|--|--|--\n")
    for spiller in assist:
        for element in spiller:
            slutt_fil.write(str(element) + "|")
        slutt_fil.write("\n")
    slutt_fil.close()

    if eliteserien :
        slutt_fil = open("eliteserien-ferdig.txt", "a")
    else :
        slutt_fil = open("obos-ferdig.txt", "a")
    slutt_fil.write("\nScript for Ã¥ generere rundetrÃ¥d kan finnes [her](https://github.com/norskball/rundetrad/).")

    slutt_fil.close()

    return

def most_common(lst):
     return max(set(lst), key=lst.count)


toppliste_antall = 3
lag_antall = 16

liste_ubehandlet = []
ligatabell = []
assistkonge = []
toppscorer = []
terminliste = []
hovedrunde = []
omberammet = []
runde_nummer = 0

####Programmet starter her

sluttfil = open("eliteserien-ferdig.txt", "w")
sluttfil.write("")
sluttfil.close()

sluttfil = open("obos-ferdig.txt", "w")
sluttfil.write("")
sluttfil.close()


if path.exists("rundetråd - eliteserien.csv"):
    liste_ubehandlet = lag_liste(True)
    ligatabell = list_ligatabell(liste_ubehandlet, lag_antall)
    toppscorer = list_toppscorer(liste_ubehandlet, toppliste_antall)
    assistkonge = list_assist(liste_ubehandlet, toppliste_antall)
    terminliste = list_terminliste(liste_ubehandlet)
    runde_nummer = sjekke_hovedrunde(terminliste)
    hovedrunde = list_runde(terminliste, runde_nummer, True)
    omberammet = list_runde(terminliste, runde_nummer, False)
    skriv_ut(ligatabell, hovedrunde, omberammet, toppscorer, assistkonge, True)
    print("Eliteserien-tråd laget.")
    os.remove("rundetråd - eliteserien.csv")
else:
    print("Finner ikke regneark for Eliteserien.")

if path.exists("rundetråd - 1. divisjon.csv"):
    liste_ubehandlet = lag_liste(False)
    ligatabell = list_ligatabell(liste_ubehandlet, lag_antall)
    toppscorer = list_toppscorer(liste_ubehandlet, toppliste_antall)
    assistkonge = list_assist(liste_ubehandlet, toppliste_antall)
    terminliste = list_terminliste(liste_ubehandlet)
    runde_nummer = sjekke_hovedrunde(terminliste)
    hovedrunde = list_runde(terminliste, runde_nummer, True)
    omberammet = list_runde(terminliste, runde_nummer, False)
    skriv_ut(ligatabell, hovedrunde, omberammet, toppscorer, assistkonge,False)
    print("OBOS-tråd laget.")
    if os.path.exists("rundetråd - 1. divisjon.csv"):
        os.remove("rundetråd - 1. divisjon.csv")
    else:
        print("Filen eksisterer ikke.")
else:
    print("Finner ikke regneark for 1. divisjon.")

print("Ferdig!")