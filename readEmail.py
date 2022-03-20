'''
Działanie skryptu:
- Dostęp do skrzynki Gmail
- Pobranie wszystkich nieprzeczytanych wiadomości
- Pobieranie szczegółów (Date, Sender, Subject, Snippet, Body)
- Oznaczanie wiadomości jako przeczytane - żeby nie czytać ich ponownie
'''

'''
Przed uruchomieniem skryptu, użytkownik powinien otrzymać autoryzację z poniższego linku:
https://developers.google.com/gmail/api/quickstart/python
Ponadtio, plik credentials.json powinien zostać zapisany we wspólnym katalogu
'''

# Importowanie potrzebnych bibliotek
from apiclient import discovery
from apiclient import errors
from httplib2 import Http
from oauth2client import file, client, tools
import base64
from bs4 import BeautifulSoup
import re
import time
import dateutil.parser as parser
from datetime import datetime
import datetime
import csv


# Tworzenie pliku storage.JSON z informacjiami o autoryzacji
SCOPES = 'https://www.googleapis.com/auth/gmail.modify'
def main():
	store = file.Storage('storage.json')
	creds = store.get()
	if not creds or creds.invalid:
		flow = client.flow_from_clientsecrets('credentials.json', SCOPES)
		creds = tools.run_flow(flow, store)
	GMAIL = discovery.build('gmail', 'v1', http=creds.authorize(Http()))

	user_id =  'me'
	label_id_one = 'INBOX'
	label_id_two = 'UNREAD'

	# Pobieranie nowych wiadomości ze szkrzynki
	unread_msgs = GMAIL.users().messages().list(userId='me',labelIds=[label_id_one, label_id_two]).execute()
	if 'messages' in unread_msgs:
		mssg_list = unread_msgs['messages']
	else:
		exit()


	print ("Total unread messages in inbox: ", str(len(mssg_list)))

	final_list = [ ]


	for mssg in mssg_list:
		temp_dict = { }
		m_id = mssg['id'] # pobieranie id pojedynczej wiadomośći
		message = GMAIL.users().messages().get(userId=user_id, id=m_id).execute() # pobieranie wiadomości przy użyciu API
		payld = message['payload'] # pobieranie payloadu wiadomości
		headr = payld['headers'] # pobieranie nagłówka


		for one in headr: # pobieranie tematu wiadomości
			if one['name'] == 'Subject':
				msg_subject = one['value']
				temp_dict['Subject'] = msg_subject
			else:
				pass


		for two in headr: # pobieranie daty
			if two['name'] == 'Date':
				msg_date = two['value']
				date_parse = (parser.parse(msg_date))
				m_date = (date_parse.date())
				temp_dict['Date'] = str(m_date)
			else:
				pass

		for three in headr: # pobieranie Nadawcy
			if three['name'] == 'From':
				msg_from = three['value']
				temp_dict['Sender'] = msg_from
			else:
				pass

		temp_dict['Snippet'] = message['snippet'] # pobieranie snippetu wiadomości


		try:

			# Pobieranie sekcji body wiadomości
			mssg_parts = payld['parts']
			part_one  = mssg_parts[0]
			part_body = part_one['body'] # pobieranie sekcji body wiadomości
			part_data = part_body['data'] # pobieranie danych z sekcji body
			clean_one = part_data.replace("-","+") # dekodowanie z Base64 na UTF-8
			clean_one = clean_one.replace("_","/") # dekodowanie z Base64 na UTF-8
			clean_two = base64.b64decode (bytes(clean_one, 'UTF-8')) # dekodowanie z Base64 na UTF-8
			soup = BeautifulSoup(clean_two , "lxml" )
			mssg_body = soup.body()

			temp_dict['Message_body'] = mssg_body

		except :
			pass

		print (temp_dict)
		final_list.append(temp_dict) # Tworzenie słownika w końcowej liście

		# Oznaczanie wiadomości jako przeczytane
		GMAIL.users().messages().modify(userId=user_id, id=m_id,body={ 'removeLabelIds': ['UNREAD']}).execute()




	print ("Total messaged retrived: ", str(len(final_list)))

	#eksportowanie wiadomości do .csv
	with open('CSV_NAME.csv', 'w', encoding='utf-8', newline = '') as csvfile:
		fieldnames = ['Sender','Subject','Date','Snippet','Message_body']
		writer = csv.DictWriter(csvfile, fieldnames=fieldnames, delimiter = ',')
		#writer.writeheader()
		for val in final_list:
			writer.writerow(val)

if __name__ == '__main__':
    main()