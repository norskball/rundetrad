import locale, os, csv
from datetime import datetime, timedelta
from collections import Counter

FEILMELDINGER = []
try:
    import requests
    AUTO_HENT = True            ### Kan settes til False for å skru av at skriptet prøver å hente regneark selv
except ImportError:
    FEILMELDINGER.append(f"{datetime.now().replace(microsecond=0)}\t-\t"
                         f"Mangler requests-biblioteket for å laste ned regneark automatisk.\n")
    AUTO_HENT = False

### Hvor mange dager fram og tilbake skriptet skal lete etter kamper
OMBERAMMEDE_MAX = 10
HOVEDRUNDE_MAX = 7
HOVEDRUNDE_MIN = -2

### Hvor mange fra hver kategori som skal tas med
MAX_ANTALL = { 'TOPPSCORER' : 5,
               'ASSIST' : 3,
               'MÅLPOENG' : 0,
                }

### Sett til True for å slette gamle rundetråder, og regneark etter bruk.
### NB! Dette sletter ALLE filer av typen '.txt' og '.csv' fra samme mappe som skriptet ligger i,
### så ikke dump skriptet rett i Mine Dokumenter om du skrur på disse. Ha skriptet i en egen mappe.
SLETT_REGNEARK = False
SLETT_TEKSTFILER = False

# ID og GIDs til google sheets
ARK_ID = ( '19DUJcGRobgWrMwkZd4efmbBCrpwe4HLEagG0z5chbpM', )
REGNEARK = { '19DUJcGRobgWrMwkZd4efmbBCrpwe4HLEagG0z5chbpM' : ( '0', '35632039' ), }

### For testing
NY_TID = datetime(2024, 5, 5, 17, 5, 0)
TESTE_TID = False

### Konstanter brukt i koden
IKKE_STARTA = 0
PÅBEGYNT = -1
FERDIGSPILT = 1

class Spiller:

    def __init__(self, liste):
        self.plassering = saniter(liste[0])
        self.navn = liste[1]
        self.mål, self.assist, self.målpoeng = saniter(liste[2]), saniter(liste[3]), saniter(liste[4])
        self.klubb = liste[5]

    def utskrift(self, kategori):
        liste = [self.plassering, self.navn, hent_flair(self.klubb)]
        streng = ''
        if kategori == 'TOPPSCORER':
            liste.append(self.mål)
        elif kategori == 'ASSIST':
            liste.append(self.assist)
        else:
            for stat in [self.mål, self.assist, self.målpoeng]:
                liste.append(stat)
        for element in liste:
            streng += str(element) + '|'
        return streng + '\n'

class Lag:

    def __init__(self, liste):
        self.plassering = saniter(liste[0])
        self.klubb = liste[1]
        self.kamper = saniter(liste[2])
        self.seire, self.uavgjort, self.tap = saniter(liste[3]), saniter(liste[4]), saniter(liste[5])
        self.mål, self.innslupne, self.poeng = saniter(liste[6]), saniter(liste[7]), saniter(liste[9])
        self.målforskjell = self.mål - self.innslupne

    def utskrift(self):
        plussminus = f"{self.målforskjell:+}" if (self.målforskjell != 0) else self.målforskjell

        liste = [self.plassering, hent_flair(self.klubb), self.kamper, self.seire, self.uavgjort, self.tap,
                 self.mål, self.innslupne, plussminus, self.poeng]
        streng = ''
        for element in liste:
            streng += str(element) + '|'

        return streng + '\n'

class Tid:

    def __init__(self, datotid):
        #dd.mm.åååå-tt.mm
        self.tid = self.dato_format(datotid)
        self.dag = self.tid.strftime('%a')
        self.dato = self.tid.strftime('%d. %b')
        self.time = self.tid.strftime('%H.%M')

    def dato_format(self, dato_str):
        tid_obj = datetime.strptime(dato_str, '%d.%m.%Y-%H.%M')
        return tid_obj

class Kamp:

    def __init__(self, liste):
        self.runde = saniter(liste[0])
        self.hjemmelag = liste[4]
        self.bortelag = liste[6]
        self.resultat = liste[5]
        self.kampstart = Tid(liste[1] + '-' +liste[3])
        self.tid = self.kampstart.tid
        self.url = liste[10]

    def utskrift(self, omberammet):
        ukedag = self.kampstart.dag.replace('.', '')
        dato = str(ukedag + ' ' + self.kampstart.dato)
        avlyst = ['Kansellert', 'Utsatt']

        if self.resultat in avlyst:
            resultat = '[' + self.resultat + '](' + self.url + ')'
        elif påbegynt_kamp(self.tid) == IKKE_STARTA:
            resultat = '[' + self.kampstart.time + '](' + self.url + ')'
        elif påbegynt_kamp(self.tid) == PÅBEGYNT:
            resultat = '([' + self.resultat + '](' + self.url + '))'
        else:
            resultat = '[' + self.resultat + '](' + self.url + ')'

        kolonner = [self.runde, dato , hent_flair(self.hjemmelag), resultat, hent_flair(self.bortelag)]

        if not omberammet:
            kolonner.remove(self.runde)

        streng = ''
        for element in kolonner:
            streng += str(element) + '|'

        return streng + '\n'

def hent_regneark():
    for id in ARK_ID:
        for ark in REGNEARK[id]:
            lenke = f'https://docs.google.com/spreadsheets/d/{id}/export?format=csv&gid={ark}'
            respons = requests.get(lenke)

            if respons.status_code == 200:
                with open(f'{id[:8]}_{ark[:8]}.csv', 'wb') as csv_fil:
                    csv_fil.write(respons.content)
            else:
                FEILMELDINGER.append(f"{datetime.now().replace(microsecond=0)}"
                                     f"\t-\tKlarte ikke hente regneark fra URL.\nURL: {lenke}\n")
    return

def behandle_csv(file):
    kategorier = ['LIGA', 'TABELL', 'TOPPSCORER', 'ASSIST', 'MÅLPOENG', 'KAMPER']
    resultat = {}
    avbryt = False

    with open(file, "r", encoding='utf-8') as csv_file:
        reader = csv.reader(csv_file)

        for kategori in kategorier:
            funnet, data = lag_liste(reader, kategori)
            if funnet:
                sanitert_data = saniter_liste(data)
                resultat[kategori] = lag_datatype(kategori, sanitert_data)
            else:
                resultat[kategori] = None
                avbryt = True
    return avbryt, resultat

def lag_liste(reader, query):
    liste = []
    funnet = False

    for row in reader:
        if row[0].upper() == query:
            funnet = True
            if query == 'LIGA':
                liste.append([row[1]])
                return funnet, liste
            else:
                next(reader)
                continue
        if funnet:
            if row[0].isdigit():
                _ = [col for col in row if col]
                liste.append(_)
            else:
                funnet = funnet if len(liste) > 0 else False
                return funnet, liste

    return funnet, liste

def lag_datatype(type, liste):
    data = []
    if type == 'KAMPER':
        for kamp in liste:
            data.append(Kamp(kamp))
    elif type == 'TABELL':
        for lag in liste:
            data.append(Lag(lag))
    elif type in ['TOPPSCORER', 'ASSIST', 'MÅLPOENG']:
        for spiller in liste:
            data.append(Spiller(spiller))
    else:
        data = liste[0]
    return data

def lag_kampprogram(liste):
    tid_nå = NY_TID if TESTE_TID else datetime.now()
    hovedrnd = finn_hovedrunde(liste)
    hoved, andre = [], []

    for kamp in liste:
        d_dager = int(kamp.tid.strftime('%j')) - int(tid_nå.strftime('%j'))
        if d_dager in range(-2, OMBERAMMEDE_MAX, 1) and kamp.runde is not hovedrnd+1:
            if kamp.runde is hovedrnd:
                hoved.append(kamp)
            else:
                andre.append(kamp)
    kampliste = [hoved, andre]
    return hovedrnd, kampliste

def lag_topplister(hoved, dict_lister):
    kategorier = {'TOPPSCORER': [], 'ASSIST' : [], 'MÅLPOENG' : []}

    for kategori in kategorier:
        if dict_lister[kategori] and hoved != 1:
            for spiller in dict_lister[kategori]:
                if len(kategorier[kategori]) < MAX_ANTALL[kategori]:
                    kategorier[kategori].append(spiller)
                else:
                    continue
    return kategorier

def finn_hovedrunde(liste):
    runde = []
    tid_nå = NY_TID if TESTE_TID else datetime.now()

    for kamp in liste:
        d_tid = int(kamp.tid.strftime('%j')) -int(tid_nå.strftime('%j'))
        if d_tid in range(HOVEDRUNDE_MIN, HOVEDRUNDE_MAX, 1):
            runde.append(kamp.runde)

    teller = Counter(runde).most_common()

    if len(teller) >= 2:
        rnd = int(teller[1][0]) if int(teller[0][0]) == int(teller[1][0])+1 else int(teller[0][0])
    else:
        rnd = int(teller[0][0]) if len(teller) == 1 else None

    return rnd

def hent_flair(str_inn):
    flairs = ['aalesund', 'aasane', 'bodoe-glimt', 'brann', 'bryne', 'fredrikstad', 'hamkam', 'haugesund', 'hoedd',
        'jerv', 'kfum-oslo', 'kongsvinger', 'kristiansund-bk', 'lillestroem', 'lyn', 'mjoendalen', 'molde', 'moss',
        'odd', 'ranheim-tf', 'raufoss', 'rosenborg', 'sandefjord', 'sandnes-ulf', 'sarpsborg-08', 'sogndal', 'stabaek',
        'start', 'stroemmen', 'stroemsgodset', 'tromsoe', 'ullensaker-kisa', 'vaalerenga', 'viking']
    unntak = {'Kristiansund': 'kristiansund-bk', 'Sandefjord Fotball': 'sandefjord', 'Ranheim': 'ranheim-tf'}
    flair_dict = {'Æ': 'ae', 'Ø': 'oe', 'Å': 'aa', '/': '-', ' ': '-'}
    flair = ''

    if str_inn in unntak:
        str_ut = f"[](/flair-{unntak[str_inn]}){str_inn}"
    else:
        for s in str_inn:
            flair = flair + flair_dict[s.upper()] if s.upper() in flair_dict else flair + s.lower()
        str_ut = f"[](/flair-{flair.lower()}){str_inn}" if flair in flairs else f"[](/flair-tom){str_inn}"

    return str_ut

def påbegynt_kamp(kampstart):
    status = IKKE_STARTA
    tid_nå = NY_TID if TESTE_TID else datetime.now()
    kampslutt = kampstart + timedelta(minutes=105)
    if tid_nå > kampstart:
        status = FERDIGSPILT if (tid_nå > kampslutt) else PÅBEGYNT
    return status

def påbegynt_runde(kampliste):
    ingen_starta, alle_ferdig = True, True

    for kampstart in kampliste:
        kamp = påbegynt_kamp(kampstart.tid)
        if kamp != IKKE_STARTA:
            ingen_starta = False
        if kamp != FERDIGSPILT:
            alle_ferdig = False
    if alle_ferdig or ingen_starta:
        return FERDIGSPILT if alle_ferdig else IKKE_STARTA
    else:
        return PÅBEGYNT

def saniter_liste(liste):
    liste = [[saniter(kolonne) for kolonne in rad] for rad in liste]
    return liste

def saniter(str_x):
    ordbok = {'Sandefjord Fotball' : 'Sandefjord', 'KFUM' : 'KFUM Oslo', 'Ranheim TF' : 'Ranheim'}
    str_x = ordbok[str_x] if str_x in ordbok else str_x

    if isinstance(str_x, str):
        str_x = str_x.replace('−', '-').strip()
    try:
        str_x = int(str_x)
    except ValueError:
        pass
    return str_x

def tøm_mappe(mappe, ext):
    for fil in os.listdir(mappe):
        if fil.endswith(ext):
            os.remove(fil)
    return

def feilmeldinger(reset = False):
    global FEILMELDINGER
    if len(FEILMELDINGER) > 0:
        with open(f"feilmeldinger.txt", "a", encoding='utf-8') as feilfil:
            for feil in FEILMELDINGER:
                feilfil.write(feil)
    FEILMELDINGER = []
    return

def prosedyre(file):
    _, dict_lister = behandle_csv(file)
    hoved, kamper = lag_kampprogram(dict_lister['KAMPER'])
    topplister = lag_topplister(hoved, dict_lister)
    skriv_ut(kamper, topplister, dict_lister)
    return

def skriv_ut(runder, topplister, dict_lister):
    tabell = dict_lister['TABELL']
    liga = dict_lister['LIGA'][0].lower()
    liga_format = '#' if liga.upper() == 'ELITESERIEN' else ''
    rundestatus = påbegynt_runde(runder[0])

    if rundestatus == PÅBEGYNT:
        status = f"per {datetime.now().strftime("%A %d.%m (kl. %H:%M)")}"
    else:
        status = "etter runden" if rundestatus == FERDIGSPILT else "før runden"

    with open(f"{liga}-ferdig.txt", "w", encoding='utf-8') as tekstfil:
        tekstfil.write(f"# Tabell {status}\n#####{liga_format}[](http://reddit.com#)\n")
        tekstfil.write("Nr | Lag | K | S | U | T | + | - | + / - | P |\n" +
                     "--- | --- | ---- | ----: | ----: | ----: | ----: | ----: | ----: | ----: |\n")
        for lag in tabell:
            tekstfil.write(lag.utskrift())

        for n, runde in enumerate(runder):
            (str1, str2, str3) = ('Omberammede', 'Runde|', ':----:|') if n else ('Rundens', '', '')
            if runde:
                tekstfil.write(f"#{str1} kamper\nDato|{str2}Hjemmelag||Bortelag|\n---|{str3}----|:----:|----|\n")
                for kamp in runde:
                    tekstfil.write(kamp.utskrift(n))
            if n == 0 and len(runde) == 0:
                FEILMELDINGER.append(f"{datetime.now().replace(microsecond=0)}\t-\tFant ingen kommende hovedrunde for {liga}.\n")

        for toppliste in topplister:
            if topplister[toppliste]:
                str1 = 'A' if toppliste == 'ASSIST' else 'M'
                (str2, str3) = ( 'A | P |', '|--|--' ) if toppliste == 'MÅLPOENG' else ( '', '' )
                tekstfil.write(f"#{toppliste.capitalize()}\nNr | Spiller | Lag | {str1} | {str2} \n"
                               f"---|:--|:--|--|--{str3}\n")
                for spiller in topplister[toppliste]:
                    tekstfil.write(spiller.utskrift(toppliste))

        tekstfil.write(
            "\n^Script ^for ^å ^generere ^rundetråd ^kan ^finnes ^[her](https://github.com/norskball/rundetrad/).")

    return

def main():
    try:
        locale.setlocale(locale.LC_TIME, 'no_NO')
    except locale.Error:
        FEILMELDINGER.append(f"{datetime.now().replace(microsecond=0)} - "
                             f"Finner ikke 'no_NO', formatteringen av norske bokstaver kan bli feil.\n")
        locale.setlocale(locale.LC_TIME, 'no_NO.UTF-8')
    dir = os.path.dirname(os.path.abspath(__file__))

    if SLETT_TEKSTFILER:
        tøm_mappe(dir, '.txt')
    else:
        tøm_mappe(dir, 'feilmeldinger.txt')

    if AUTO_HENT:
        hent_regneark()
    feilmeldinger(reset=True)

    for file in os.listdir(dir):
        if file.endswith('.csv'):
            prosedyre(file)

    if SLETT_REGNEARK:
        tøm_mappe(dir, '.csv')

    feilmeldinger()

    return

if __name__ == '__main__':
    main()
