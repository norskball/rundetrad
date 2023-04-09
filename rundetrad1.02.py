import datetime
import os
from os import path


toppliste_antall = 3
lag_antall = 16


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


def main():

    clear_txt()

    # Eliteserien
    if path.exists("rundetråd - eliteserien.csv"):
        prosedyre(True)
        print("Eliteserien-tråd laget.")
        os.remove("rundetråd - eliteserien.csv")
    else:
        print("Finner ikke regneark for Eliteserien.")

    # 1. Divisjon
    if path.exists("rundetråd - 1. divisjon.csv"):
        prosedyre(False)
        print("OBOS-tråd laget.")
        os.remove("rundetråd - 1. divisjon.csv")
    else:
        print("Finner ikke regneark for 1. divisjon.")

    print("Ferdig!")
    return


def lag_liste(eliteserien):
    tabell = []
    if eliteserien:
        file = open("rundetråd - eliteserien.csv", "r")
    else:
        file = open("rundetråd - 1. divisjon.csv", "r")
    for line in file:
        line_replace = line.replace(",,", "")
        line_strip = line_replace.strip()
        lag = line_strip.split(",")
        tabell.append(lag)
    file.close()
    return tabell


def prosedyre(eliteserien):
    liste_ubehandlet = lag_liste(eliteserien)
    ligatabell = list_ligatabell(liste_ubehandlet)
    terminliste = list_terminliste(liste_ubehandlet)
    runde_nummer = sjekke_hovedrunde(terminliste)
    if (int(runde_nummer) != 1):
        toppscorer = list_toppscorer(liste_ubehandlet)
        assistkonge = list_assist(liste_ubehandlet)
    else:
        toppscorer = 0
        assistkonge = 0
    hovedrunde = list_runde(terminliste, runde_nummer, True)
    omberammet = list_runde(terminliste, runde_nummer, False)
    skriv_ut(ligatabell, hovedrunde, omberammet, toppscorer, assistkonge, eliteserien)
    return


def list_ligatabell(liste):

    tabell = []
    for streng in liste:
        substring = "Tabell"
        if substring in streng:
            k = 1
            while k <= lag_antall:
                tabell.append(liste[k + 1])
                k += 1
    for lag in tabell:
        for element in lag:
            if element == "":
                lag.pop(lag.index(element))
    tabell = formater_tabell(tabell)
    return tabell


def clear_txt():
    fil = open("eliteserien-ferdig.txt", "w")
    fil.write("")
    fil.close()

    fil = open("obos-ferdig.txt", "w")
    fil.write("")
    fil.close()
    return


def list_terminliste(liste):
    liste_ut = []
    substring = "element.do"
    for streng in liste:
        for element in streng:
            if substring in element:
                liste_ut.append(streng)
            else:
                pass
    liste_ut = formater_terminliste(liste_ut)
    return liste_ut


def list_toppscorer(liste):
    substring = "Toppscorer"
    liste_scorer = []
    index = index_2d(liste, substring)
    for spiller in liste[index[0] + 2:index[0] + 5]:
        liste_scorer.append(spiller)
        if spiller[2] in flair:
            spiller[2] = flair.get(spiller[2])
        else:
            spiller[2] = flair.get("Default")+spiller[2]
    return liste_scorer


def index_2d(my_list, v):
    for i, x in enumerate(my_list):
        if v in x:
            return i, x.index(v)


def list_assist(liste):
    substring = "Assistkonge"
    assist_liste = []
    index = index_2d(liste, substring)
    for spiller in liste[index[0] + 2:index[0] + 5]:
        assist_liste.append(spiller)
        if spiller[2] in flair:
            spiller[2] = flair.get(spiller[2])
        else:
            spiller[2] = flair.get("Default") + spiller[2]
    return assist_liste


def list_runde(liste, nummer, hoved):
    runde_liste = []
    dageni_dag = datetime.datetime.now()
    dato = 0
    for kamp in liste:
        dag_nummer = datetime.datetime(int(kamp[dato][6:10]), int(kamp[dato][3:5]), int(kamp[dato][0:2]))
        dag_nummer = dag_nummer.strftime("%j")
        # Inkluderer neste hovedrunde
        if hoved:
            if int(dag_nummer) - int(dageni_dag.strftime("%j")) in range(-2, 7, 1) and int(kamp[1]) == int(nummer):
                runde_liste.append(kamp)
        # Inkluderer kamper den neste uken++ som ikke tilhører inneværende eller neste runde.
        else:
            if int(dag_nummer) - int(dageni_dag.strftime("%j")) in range(0, 10, 1) and int(kamp[1]) != int(nummer)\
                    and int(kamp[1]) != int(nummer) + 1:
                runde_liste.append(kamp)
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
        # Legger til manglende datoer. Index 0 = dato
        if len(kamp[0]) != 0:
            dato_minne = kamp[0]
        else:
            kamp[0] = dato_minne

        # Formaterer rundenummer. Index 1 = rundenummer
        if ". runde" in kamp[1]:
            kamp[1] = kamp[1].replace(". runde", "")

        # Index 2 = hjemmelag
        kamp[2] = flair.get(kamp[2]) if kamp[2] in flair else flair.get("Default")+kamp[2]

        # Index 3 = avspark
        kamp[3] = f"[{kamp[3]}]"

        # Index 4 = URL
        kamp[4] = f"(http://altomfotball.no/altomfotball.no{kamp[4]})"
        kamp[3] = kamp[3] + kamp[4]
        kamp.pop(4)

        # Index 4 = bortelag
        kamp[4] = flair.get(kamp[4]) if kamp[4] in flair else flair.get("Default")+kamp[4]

    return liste


def sjekke_hovedrunde(liste):
    dato = 0
    runde = []
    dageni_dag = datetime.datetime.now()
    for kamp in liste:
        dag_nummer = datetime.datetime(int(kamp[dato][6:10]), int(kamp[dato][3:5]), int(kamp[dato][0:2]))
        dag_nummer = dag_nummer.strftime("%j")
        if int(dag_nummer) - int(dageni_dag.strftime("%j")) in range(-2, 7, 1):
            runde.append(kamp[1])
    return most_common(runde)


def skriv_ut(tabell, runde, ekstra, maal, assist, eliteserien):

    # Tabell
    if eliteserien:
        ut_fil = open("eliteserien-ferdig.txt", "a")
        ut_fil.write("# Tabell fÃ¸r runden\n######[](http://reddit.com#)\n")
    else:
        ut_fil = open("obos-ferdig.txt", "a")
        ut_fil.write("# Tabell fÃ¸r runden\n#####[](http://reddit.com#)\n")

    ut_fil.write("Nr | Lag | K | S | U | T | + | - | + / - | P |\n" +
                 "--- | --- | ---- | ----: | ----: | ----: | ----: | ----: | ----: | ----: |\n")
    for lag in tabell:
        for element in lag:
            ut_fil.write(str(element)+"|")
        ut_fil.write("\n")

    # Rundens kamper
    ut_fil.write("#Rundens kamper\nDato|Hjemmelag||Bortelag|Kanal\n---|----|:----:|----|----\n")
    for kamp in runde:
        for element in kamp:
            if kamp.index(element) == 1:
                pass
            else:
                ut_fil.write(str(element)+"|")
        ut_fil.write("\n")

    # Omberammede kamper
    if ekstra:
        ut_fil.write("#Omberammede kamper\nDato|Runde|Hjemmelag||Bortelag|Kanal\n" +
                     "---|:----:|----|:----:|----|----\n")
    for kamp in ekstra:
        for element in kamp:
            ut_fil.write(str(element)+"|")
        ut_fil.write("\n")

    # Toppscorer
    if (maal != 0):
        ut_fil.write("#Toppscorer\nNr | Spiller | Lag | M | K | \n---|:--|:--|--|--|--\n")
        for spiller in maal:
            for element in spiller:
                ut_fil.write(str(element)+"|")
            ut_fil.write("\n")

    # Assist
    if (assist != 0):
        ut_fil.write("#Assist\nNr | Spiller | Lag | A | K | \n---|:--|:--|--|--|--\n")
        for spiller in assist:
            for element in spiller:
                ut_fil.write(str(element) + "|")
            ut_fil.write("\n")

    ut_fil.write("\nScript for Ã¥ generere rundetrÃ¥d kan finnes [her](https://github.com/norskball/rundetrad/).")
    ut_fil.close()

    return


def most_common(lst):
    return max(set(lst), key=lst.count)


main()