import os, calendar, datetime, pickle, smtplib
from math import floor
Dni_Tygodnia = []
Dni = {}
Przedmioty = {}
Dni_nazwy = ["poniedzialek", "wtorek", "sroda", "czwartek", "piatek", "sobota", "niedziela"]

pomoc = """POMOC
Opis funkcji:
    0. Wrazie jak po nacisnieciu nacisnij enter aby kontynuowac nic sie nie stanie
    1. Wyœwietla plan lekcji w danym tygodniu
    2. Wyœwietla kalendarz z (1) lub bez(2) obecnoœci
    3. Pokazuje dany dzieñ w kalendarzu wraz z obecnosciami
    4. Daje mo¿liwoœæ zmiany obecnoœci na lekcjach w danym dniu
        - mozna ustawic calo dniowa nieobecnosc kwybierajac n lub wybrac recznie (w)
    5. Daje mo¿liwoœæ ustawienia dni w których dodatkowo poza weekendami nie odbywaja sie zajêcia w szkole
    6. Podaje informacje o przedmiocie:
        - % obecnosci do dzis - 100% * (ilosc obecnosci do dzis)/(ilosc lekcji ktore sie do dzis odbyly)
        - calkowity % obecnosci w roku - 100% * (ilosc obecnosci do dzis)/(ilosc godzin przedmiotu w roku)
    7. Wyswietla informacje:
        - jezeli na jakis przedmot nie trzeba juz chodzic (calkowity % obecnosci w roku > 0.51)
        - jezeli na danym przedmiocie jest mniej niz 51% obecnosci do dzis
    8. Wyswietla ilosc dni do konca semestru
    9. Moza wyslac email do tworcy (nie dziala)
    10. Wswietla pomoc
    11. Pozwala zmieniæ dan¹ lekcje w danym dniu gdy np zamiast hisu byla matma
    12. Tworzy nowy plan od podanego dnia
    13. Tworzy kopie obecnosci, dni wolnych i lekcji w takiej postaci ze mozna ja wkleic w dana funkcje zeby wrazie co nie trzeba bylo wszystkiego przepisywac
"""

class DniTygodnia:
    def __init__(self, nr_dnia):
        if nr_dnia <= 4:
            self.szkola = True
        else:
            self.szkola = False
        self.lekcje = []
        self.nr_dnia = nr_dnia

    def ustaw_lekcje(self):
        global Dni_Tygodnia
        if self.szkola is True:
            self.lekcje = []
            os.system("cls")
            print("wpisz lekcje po kolei  (rekomendowane: mat / fiz / inf / pol / ang / nie / rus / his / atk / rel "
                  "/ wuf/ zzw / wos / wok / geo / bio / chem) koniec - enter")
            n = 0
            while True:
                lekcja = input("Lekcja nr : " + str(n) + " w dniu: " + str(self.nr_dnia) + " => ")
                if lekcja == "":
                    break
                if lekcja not in Przedmioty:
                    Przedmioty.update({lekcja: Przedmioty_(lekcja)})
                    zap_prz()
                self.lekcje.append(lekcja)
                n += 1
            with open("Tyg.bin", "wb") as plik:
                pickle.dump(Dni_Tygodnia, plik)
            print("Lekcje w dniu", self.nr_dnia, "zostaly zapisane")
        else:
            print("W tym dniu nie ma lekcji :D")


class Dzien:
    def __init__(self, dz_tyg, dat):
        global Dni_Tygodnia
        self.dzien_tygodnia = dz_tyg
        self.data = dat
        self.szkola = Dni_Tygodnia[dz_tyg].szkola
        self.obecnosci_L = []
        self.obecnosci_O = []
        if self.szkola is True:
            for i in range(len(Dni_Tygodnia[dz_tyg].lekcje)):
                self.obecnosci_O.append("+")
                self.obecnosci_L.append(Dni_Tygodnia[dz_tyg].lekcje[i])
    def ustaw_obecnosci(self):
        if self.szkola is False:
            print("To dzien wolny !!!")
            return 0
        try:
            co = input('w - wybierz godziny nieobecnosci / n - nieobecny caly dzien')
            if co not in ['n', 'N', 'W', 'w']:
                raise ValueError
        except ValueError:
            print("dokonaj dobrego wyboru!!!")
            return 0
        if co in ['w', "W"]:
            print("\"+\" - obecny / \"0\" - brak zajec / - \"-\" nie obecny  ")
        for lekcja in range(len(self.obecnosci_L)):
            if co in ['w', "W"]:
                wart_ob = input(self.obecnosci_L[lekcja] + " ob: ")
            if co in ['n', "N"]:
                wart_ob = "-"
            try:
                if wart_ob not in ["+", "0", "-"]:
                    raise ValueError("zly typ")
            except ValueError or UnboundLocalError:
                print(": WARTOSC Z POZA PRZEDZIALU LUB ZLY TYP - zmien obecnosci jeszcze raz")
                return 0
            self.obecnosci_O[lekcja] = wart_ob
            zap_kal()


class Przedmioty_:
    def __init__(self, nazwa):
        self.nazwa = nazwa
        self.ilosc_calkowita = 0.1
        self.odbyte = 0
        self.do_odbycia = 0
        self.jeszcze = 0
        self.procent_obecny = 0
        self.ilosc_calkowita_do_dzis = 0.1
        self.procent = 0
        self.ilosc_nieobecnosci = 0

    def oblicz_ilosc(self):
        suma = 0
        for i in Dni:
            if Dni[i].szkola is True:
                for j in range(len(Dni[i].obecnosci_L)):
                    if Dni[i].obecnosci_L[j] == self.nazwa:
                        if Dni[i].obecnosci_O[j] != 0:
                            suma += 1
        self.ilosc_calkowita = suma
        self.procent = self.odbyte / self.ilosc_calkowita
        self.do_odbycia = self.ilosc_calkowita - self.ilosc_calkowita_do_dzis
        self.jeszcze = abs(floor(-self.ilosc_calkowita * 0.51)) - self.odbyte
        zap_prz()

    def oblicz_ilosc_do_dzis(self):
        suma = 0
        dzis = datetime.datetime.now()
        do = str(dzis.day) + '.' + str(dzis.month) + '.' + str(dzis.year)
        for i in Dni:
            if Dni[i].szkola is True:
                for j in range(len(Dni[i].obecnosci_L)):
                    if Dni[i].obecnosci_L[j] == self.nazwa:
                        if Dni[i].obecnosci_O[j] != "0":
                            suma += 1
            if i == do:
                break

        self.ilosc_calkowita_do_dzis = suma
        self.procent_obecny = self.odbyte / self.ilosc_calkowita_do_dzis
        self.do_odbycia = self.ilosc_calkowita - self.ilosc_calkowita_do_dzis
        zap_prz()

    def oblicz_odbyte(self):
        suma = 0
        dzis = datetime.datetime.now()
        dzisiaj = str(dzis.day) + '.' + str(dzis.month) + '.' + str(dzis.year)
        for i in Dni:
            if Dni[i].szkola is True:
                    for j in range(len(Dni[i].obecnosci_L)):
                        if Dni[i].obecnosci_L[j] == self.nazwa and Dni[i].obecnosci_O[j] == "+":
                            suma += 1
            if i == dzisiaj:
                break

        self.odbyte = suma
        self.procent_obecny = self.odbyte / self.ilosc_calkowita_do_dzis
        self.procent = self.odbyte / self.ilosc_calkowita
        self.jeszcze = abs(floor(-self.ilosc_calkowita * 0.51)) - self.odbyte
        zap_prz()


    def jeszcze(self):
        self.jeszcze = abs(floor(-self.ilosc_calkowita * 0.51)) - self.odbyte


    def oblicz_nieobecnosci(self):
        suma = 0
        dzis = datetime.datetime.now()
        dzisiaj = str(dzis.day) + '.' + str(dzis.month) + '.' + str(dzis.year)
        for i in Dni:
            if Dni[i].szkola is True:
                for j in range(len(Dni[i].obecnosci_L)):
                    if Dni[i].obecnosci_L[j] == self.nazwa and Dni[i].obecnosci_O[j] == "-":
                        suma += 1
            if i == dzisiaj:
                break
        self.ilosc_nieobecnosci = suma
        zap_prz()

    def oblicz_procent_obecny(self):
        self.procent_obecny = self.odbyte/self.ilosc_calkowita_do_dzis
        zap_prz()

    def oblicz_procent_calkowity(self):
        self.procent = self.odbyte/self.ilosc_calkowita
        zap_prz()


    def oblicz_do_odbycia(self):
        self.do_odbycia = self.ilosc_calkowita - self.ilosc_calkowita_do_dzis
        zap_prz()


def zap_kal():
    with open("Dni.bin", 'wb') as plik1:
        pickle.dump(Dni, plik1)


def zap_prz():
    with open("Przedmioty.bin", 'wb') as plik2:
        pickle.dump(Przedmioty, plik2)

def zmien_lekcje():
    while True:
        os.system("cls")
        dzien = input("podaj date do zmiany lekcji dd.mm.rrrr  (bez zbednych zer)/ enter - koniec: ")
        if dzien == "":
            return 0
        try:
            if Dni[dzien].szkola is True:
                print("lekcje w dniu [0,1,2...]: ", Dni[dzien].obecnosci_L)
                output = ""
                for i in Przedmioty:
                    output += str(Przedmioty[i].nazwa) + ", "
                print("Dostepne lekcje: ", output)
            else:
                print("to dzien bez szkoly! ")
                return 0
        except KeyError:
            print("nieprawidlowa data")
            continue
        while True:
            if Dni[dzien].szkola is False:
                print("To dzien wolny !!!")
                return 0
            co = input('wybierz godzine do zmiany')
            if co == "":
                break
            try:
                inp = input("zamien " + Dni[dzien].obecnosci_L[int(co)] + " na :")
                if inp not in Przedmioty:
                    raise AssertionError
                Dni[dzien].obecnosci_L[int(co)] = inp
            except AssertionError or KeyError:
                print("blednie podales lekcje")
                continue
            zap_kal()


def ustaw_dni_wolne():
    global Dni
    while True:
        dz = input("podaj date w postaci dd.mm.rrrr (bez zbednych zer)\n/ enter - koniec ")
        if dz == "":
            return 0
        try:
            wolny = input('wolny - w/ szkola - s')
            if wolny not in ['w','s']:
                raise AssertionError
        except AssertionError:
            print("zly wybor - jeszcze raz")
            continue
        try:
            if wolny == "w":
                Dni[dz].szkola = False
            elif wolny == "s":
                Dni[dz].szkola = True
        except KeyError:
            print("dzien poza kalendarzem")
            continue
        zap_kal()
        if wolny == "w":
            print("Dzien: ", Dni[dz].data, " ustawiony jako wolny")
        elif wolny == "s":
            print("Dzien: ", Dni[dz].data, " ustawiony jako szkolny")


def stworz_tydzien():
    print("""po podaniu planu i wpisaniu obecnosci oraz dni wolnych aplikacja ulatwi przetrwanie szkoly - szczegoly POMOC""")
    print("NASTAPI TWORZENIE PLANU:\n POSTEPUJ ZGODNIE Z INSTRUKCJAMI:\n")
    try:
        global Dni_Tygodnia
        Dni_Tygodnia = []
        for i in range(7):
            Dni_Tygodnia.append(DniTygodnia(i))
            if i < 5:
                Dni_Tygodnia[i].ustaw_lekcje()
        with open("Tyg.bin", "wb") as plik:
            pickle.dump(Dni_Tygodnia, plik)
    except:
        print("Blad krytyczny - cos poszlo nie tak - sproboj wpisac jeszcze raz (byc moze to problem enterow)")
    else:
        print("Nowy tydzien stworzony")


def pokaz_tydzien():
    for dzien in range(5):
        print(Dni_nazwy[dzien].upper())
        for i in range(len(Dni_Tygodnia[dzien].lekcje)):
            print("\t", i, ': ', Dni_Tygodnia[dzien].lekcje[i])


def zap_plik_ob_plan():
    obecnosci = open("obecnosci.txt", "w")
    lekcje = open("lekcje.txt", "w")
    wolne = open("wolne.txt", "w")
    for dzien in Dni:
        if Dni[dzien].szkola == True:
            obecnosci.write(Dni[dzien].data + "\nw\n")
            wolne.write(Dni[dzien].data + "\n")
            wolne.write("s\n")
            lekcje.write(Dni[dzien].data + "\n")
            for lekcja in range(len(Dni[dzien].obecnosci_L)):
                obecnosci.write(str(Dni[dzien].obecnosci_O[lekcja]) + "\n")
                lekcje.write(str(lekcja) + "\n")
                lekcje.write(Dni[dzien].obecnosci_L[lekcja] + "\n")
            lekcje.write("\n")
        else:
            wolne.write(Dni[dzien].data + "\n")
            wolne.write("w\n")
    obecnosci.close()
    lekcje.close()

def stworz_kalendarz():
    os.system("cls")
    global Dni
    print("podawaj w liczbach bez zbednych zer")
    try:
        rok_s = int(input("rok poczatku semestru: "))
        mies_s = int(input("miesiac poczatku semestru: "))
        dz_s = int(input("dzien poczatku semestru: "))
        rok_k = int(input("rok konca semestru: "))
        mies_k = int(input("miesiac konca semestru: "))
        dz_k = int(input("dzien konca semestru: "))
        if rok_s > rok_k or ((rok_s == rok_k and mies_s > mies_k) or (rok_s == rok_k and mies_s == mies_k and dz_k < dz_s)):
            raise AssertionError("blad daty")
    except ValueError:
        print("BLAD: podaj liczbe!!!")
        return 0
    except AssertionError as p:
        print(p, "blad")
        return 0

    if rok_s == rok_k:
        for mies in range(mies_s, mies_k + 1):
            for dz in calendar.Calendar().itermonthdays2(rok_s, mies):
                if (((mies == mies_s and dz[0] >= dz_s) or mies > mies_s) and ((mies == mies_k and dz[0] <= dz_k) or mies < mies_k)) and dz[0] != 0:
                    data = str(dz[0]) + "." + str(mies) + "." + str(rok_k)
                    Dni.update({data: Dzien(dz[1], data)})
    elif rok_s == rok_k-1:
        for mies in range(mies_s, 13):
            for dz in calendar.Calendar().itermonthdays2(rok_s, mies):
                if ((mies == mies_s and dz[0] >= dz_s) or mies > mies_s) and dz[0] != 0:
                    data = str(dz[0]) + "." + str(mies) + "." + str(rok_s)
                    Dni.update({data: Dzien(dz[1], data)})
        for mies in range(1, mies_k + 1):
            for dz in calendar.Calendar().itermonthdays2(rok_k, mies):
                if ((mies == mies_k and dz[0] <= dz_k) or mies < mies_k) and dz[0] != 0:
                    data = str(dz[0]) + "." + str(mies) + "." + str(rok_k)
                    Dni.update({data: Dzien(dz[1], data)})
    else:
        print("blad tworzenia kalendarza")
    zap_kal()
    print("kalendarz stworzony")


def pokaz_kalendarz():
    obec = input("1 - z obecnosciami\n2 - bez obecnosci\n")
    os.system("cls")
    if obec not in ['1', '2']:
        print("nie ma takiego wyrobu!!!")
        return 0
    for dzien in Dni:
        print("Data:", Dni[dzien].data)
        print("\t dzien tygodnia: ", Dni_nazwy[Dni[dzien].dzien_tygodnia])
        print("\t szkola: ", Dni[dzien].szkola)
        if obec == '1' and Dni[dzien].szkola is True:
            print("\t obecnosci: ")
            for lekcja in range(len(Dni[dzien].obecnosci_L)):
                print("\t\t", Dni[dzien].obecnosci_L[lekcja], " ob: ", Dni[dzien].obecnosci_O[lekcja])


def pokaz_dz():
    dzien = input("podaj date w postaci dd.mm.rrrr (bez zbednych zer)\n")
    try:
        print("Data:", Dni[dzien].data)
    except KeyError:
        print("nie ma takiego dnia")
        return 0
    print("\t dzien tygodnia: ", Dni_nazwy[Dni[dzien].dzien_tygodnia])
    print("\t szkola: ", Dni[dzien].szkola)
    print("\t obecnosci: ")
    for lekcja in range(len(Dni[dzien].obecnosci_L)):
        print("\t\tlekcja: ", Dni[dzien].obecnosci_L[lekcja], " ob: ", Dni[dzien].obecnosci_O[lekcja])


def pokaz_info_o_przedmiocie():
    print("DOSTEPNE PRZEDMIOTY:")
    output = ''
    for i in Przedmioty:
        output += str(Przedmioty[i].nazwa) + ", "
    print(output)
    przedm = input("podaj przedmiot: ")
    if przedm in Przedmioty:
        print("przedmiot:", przedm)
        print("\t", "ilosc obecnosci--------:", Przedmioty[przedm].odbyte)
        print("\t", "ilosc nieobecnosci- - -:", Przedmioty[przedm].ilosc_nieobecnosci)
        print("\t", "% obecnosci do dzis----:", round(Przedmioty[przedm].procent_obecny * 100,1), "%")
        print("\t", "ilosc lekcji ktore sie odbyly- - - - - -:", Przedmioty[przedm].ilosc_calkowita_do_dzis)
        print("\t", "ilosc lekcji ktore sie odbeda-----------:", Przedmioty[przedm].do_odbycia)
        print("\t", "calkowita ilosc godzin przedmiotu w roku:", Przedmioty[przedm].ilosc_calkowita)
        print("\t", "calkowity % obecnosci w roku------------:", floor(Przedmioty[przedm].procent * 100), "%")
    else:
        print("nie ma takiego przedmiotu")


def alerty():
    STR = ""
    Str2 = ""
    for i in Przedmioty:
        if Przedmioty[i].procent_obecny < 0.51:
            print("ARARM!!! NA PRZEDMIOCIE: ##>- " + str(i) + "-<## MNIEJ NIZ 51% OBECNOSCI:  ",
                  Przedmioty[i].procent_obecny * 100, "%")
        if Przedmioty[i].procent > 0.51:
            STR += i + " ---- " + str(round(Przedmioty[i].procent*100, 1)) + " %\n"
        else:
            Str2 += "\t" + i + " ; " + str(Przedmioty[i].jeszcze) + "\n"
    if len(STR) > 0:
        print("NIE MUSISZ JUZ CHODZIC NA :")
        print(STR)
    if len(Str2) > 0:
        print("(lekcja ; ilosc obowiazkowych obecnosci) ")
        print("MUSISZ JESZCZE CHODZIC NA :")
        print(Str2)


def aktualizacja_dzis():
    global Przedmioty
    for przedmiot in Przedmioty:
        Przedmioty[przedmiot].oblicz_ilosc()
        Przedmioty[przedmiot].oblicz_ilosc_do_dzis()
        Przedmioty[przedmiot].oblicz_odbyte()
        Przedmioty[przedmiot].oblicz_procent_obecny()
        Przedmioty[przedmiot].oblicz_procent_calkowity()
        Przedmioty[przedmiot].oblicz_do_odbycia()
        Przedmioty[przedmiot].oblicz_nieobecnosci()
    zap_prz()
def wyslij_email():
    print("!!!  funkca moze nie dzialac  !!!")
    nadawca = input("podaj swoj email: ")
    odbiorca = "kaignacy@gmail.com"
    print("napisz wiadomosc: (jako ostatnia linike wpisz : \"koniec12321\"")
    linia = ""
    text = ""
    while linia != "koniec12321":
        linia = input()
        text += linia + "\n"
    text2 = "IS-studio dziekuje za twoja informacje o aplikacji STS:\nPozdrawiam\n\n Wiadomosc wygenerowana automatycznie"
    print("wysylanie wiadomosci...")
    try:
        mail = smtplib.SMTP('localhost')
        mail.sendmail(nadawca, [odbiorca], text)
        print("email wyslany:")
    except:
        print("cos poszlo nie tak ... przepraszamy")
        return 0
    try:
        mail = smtplib.SMTP('localhost')
        mail.sendmail(odbiorca, [nadawca], text2)
    except:
        return 0

def zmiana_obecnosci():
    while True:
        data = input("podaj date w postaci dd.mm.rrrr (bez zbednych zer)\n/ enter - koniec ")
        if data == "":
            break
        try:
            Dni[data].ustaw_obecnosci()
        except KeyError:
            print("nie ma takiej daty:", data)
            break


def do_wakacji():
    dzis = datetime.datetime.now()
    dzisiaj = str(dzis.day) + '.' + str(dzis.month) + '.' + str(dzis.year)
    wszystkie = 0
    doDzis = 0
    for i in Dni:
        wszystkie += 1
    for i in Dni:
        doDzis += 1
        if i == dzisiaj:
            break
    print("Do konca semestru zostalo:\n###>>>-", wszystkie - doDzis, "-<<<###\n", "     D N I")


try:
    plik_dni_tyg = open("Tyg.bin", 'rb')
except FileNotFoundError:
    print("mozesz skorzystac z pliku: plan.txt -> poprostu go wklej i nacisnij enter jak bedzie potrzeba")
    stworz_tydzien()
else:
    Dni_Tygodnia = pickle.load(plik_dni_tyg)
try:
    plik_dni = open("Dni.bin", 'rb')
except FileNotFoundError:
    stworz_kalendarz()
else:
    Dni = pickle.load(plik_dni)
try:
    plik_przedmioty = open("przedmioty.bin", 'rb')
except FileNotFoundError:
    stworz_tydzien()
else:
    Przedmioty = pickle.load(plik_przedmioty)

aktualizacja_dzis()
while True:
    print("1 - pokaz tydzien")
    print("2 - pokaz kalendarz")
    print("3 - pokaz dzien (w kalendarzu)")
    print("4 - podaj info o przedmiocie")
    print("5 - pokaz alarmy")
    print("6 - ile dni do konca semestru")
    print("7 - ustaw dni wolne")
    print("8 - zmien obecnosci w dniu...")
    print("9 - zmien lekcje w dniu")
    print("10 - POMOC")
    print("11 - nowy plan")
    print('12 - zglos blad / ocen aplikacje / nadeslij sugestie')
    print("100 - utworz kopie danych")
    print("KONIEC -  wcisnij enter")
    funkcja = input()
    try:
        aktualizacja_dzis()
        nr = int(funkcja)
        os.system("cls")
        if nr == 0:
            nic = input("wcisnij enter ponownie")
        if nr == 1:
            pokaz_tydzien()
        if nr == 2:
            pokaz_kalendarz()
        if nr == 3:
            pokaz_dz()
        if nr == 8:
            zmiana_obecnosci()
            aktualizacja_dzis()
        if nr == 7:
            ustaw_dni_wolne()
            aktualizacja_dzis()
        if nr == 4:
            pokaz_info_o_przedmiocie()
        if nr == 5:
            alerty()
        if nr == 6:
            do_wakacji()
        if nr == 12:
            wyslij_email()
        if nr == 10:
            print(pomoc)
        if nr == 9:
            zmien_lekcje()
            aktualizacja_dzis()
        if nr == 11:
            stworz_tydzien()
            stworz_kalendarz()
            aktualizacja_dzis()
            zap_kal()
            zap_prz()
        if nr == 100:
            zap_plik_ob_plan()

    except ValueError:
        break
    else:
        nic = input("nacisnij enter aby kontynuowac")
        del nic
        os.system("cls")