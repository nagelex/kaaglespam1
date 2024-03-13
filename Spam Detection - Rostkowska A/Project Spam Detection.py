""" 
Projekt zaliczeniowy python sem. zimowy
W kodzie będę używać bibliotek: imaplib - do obsługi maila, os - do operowania ścieżkami, yaml - do przechowywania loginu i hasła, 
decode_header - do odkodowania zawartości tytułu maila.

Podstawową zasadą bezpieczeństwa jest nie zawieranie haseł w kodzie. Z tego powodu postanowiłam je zapisać w osobnym pliku, a polecaną do tego typu rzeczy
biblioteką jest yaml. Przynajmniej na bardzo podstawowym poziomie bezpieczeństwa. Wiadomo lepiej by było to zrobić przez api, ale na potrzeby zaliczenia 
kursu nie jest to konieczne. 

Na potrzeby sprawdzenia działania programu założyłam testową skrzynkę na Gmailu. Jest zabezpieczona podwójnym logowaniem, a w pliku .yml znajduje się 
dedykowane hasło dla aplikacji. Program również jest dedykowany dla gmaila, i do praktycznego zastosowania wymagałby wielu ulepszeń.

"""

# Wczytanie odpowiednich bibliotek
import imaplib
from email.header import decode_header
import os
import yaml 


# Upewnienie się, że pracujemy w odpowiednim katalogu
os.chdir(os.path.dirname(os.path.abspath(__file__)))
print("Bieżący katalog: ", os.getcwd())


def logowanie():
    with open("login.yml") as login:
        content = login.read()

    moje_dane = yaml.load(content, Loader=yaml.FullLoader)
    user, password = moje_dane["user"], moje_dane["password"]

    #adres URL do IMAP 
    imap_url = 'imap.gmail.com'
    # Połaczenie z Gmail za pomocą SSL
    my_mail = imaplib.IMAP4_SSL(imap_url)
    # Zalogowanie na maila
    my_mail.login(user, password)

    print('\nZalogowano na maila:', user )

    return my_mail

def is_spam(email_subject):
    spam_keywords = tagi
    return any(keyword in email_subject.lower() for keyword in spam_keywords)

def lower_list (wyraz):
    return wyraz.lower()

def zamknecie(my_mail):
    print('Trwa wylogowywanie...')
    my_mail.close()
    my_mail.logout()
    print('Wylogowano')



my_mail = logowanie()

# Wybór skrzynki (inbox)
my_mail.select('inbox')

# Wczytanie listy tagów, określających spam
with open ('tagi.txt','rt') as plik:
    tagi_n = plik.readlines()
tagi=[]
for i in tagi_n:
            tagi.append(i.rstrip())
tagi = list(map(lower_list, tagi))
print("\tSłowa na podstawie których wybierany jest spam:")
print(tagi)

# Liczenie całkowitej liczby maili
status, message_count = my_mail.uid('search', None, 'ALL')
if status != 'OK':
    print("Error fetching emails.\n")

num_emails = len(message_count[0].split())

if num_emails != 0:
    print(f""" \nIlość wszystkich maili znalezionych na skrzynce: {num_emails}  
            Czy chcesz rozpocząć skanowanie wszystkich wiadomości na podstawie określonych tagów? """)
    
    while True:
        odpowiedz = input(" [y/n]?  ")
        yes = ['yes','y']
        no = ['no','n']

        if odpowiedz.lower() in yes:
            print ('Skanowanie...')

            status, email_ids = my_mail.uid('search', None, 'ALL')
            if status != 'OK':
                print("Nie udało się pobrać listy emaili.")
                exit(1)

            emails = email_ids[0].split()
            spam_count = 0

            for email_id in emails:
                # Pobieranie tytułu maila
                status, email_data = my_mail.uid('fetch', email_id, '(BODY.PEEK[HEADER.FIELDS (SUBJECT)])')
                if status != 'OK':
                    print("Nie udało się pobrać danych emaila.")
                    continue  # Pominięcie maila i przejście do następnego

                subject_header = email_data[0][1].decode()
                subject = decode_header(subject_header)[0][0]
                if isinstance(subject, bytes):
                    subject = subject.decode()
                    print (email_id, subject_header)

                if is_spam(subject):
                    spam_count += 1
                    
                    # Przeniesienie maila do folderu Spam (nazwa może się różnić na einnych skrzynkach)
                    result, _ = my_mail.uid('COPY', email_id, '[Gmail]/Spam')
                    if result == 'OK':
                        my_mail.uid('store', email_id, '+FLAGS', '\\Deleted')
            my_mail.expunge()


            print(f"Liczba wykrytych spamowych emaili: {spam_count}")
            break

        elif odpowiedz.lower() in no:
            print ('Eh, twoja strata...'),
            break

        else:
            print ('Proszę wybrać: tak (y) lub nie (n)')
            continue

else:
     print("Nie znaleziono żadnych maili\n")

zamknecie(my_mail)
