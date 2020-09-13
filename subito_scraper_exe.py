import requests
from bs4 import BeautifulSoup
import os.path
import json
import smtplib
import time



queries = dict()
dbFile = 'tracked_searches'
starttime=time.time()


def load_file(fileName):
    global queries
    if not os.path.isfile(fileName):
        return
    with open(fileName) as file:
        queries = json.load(file)

def save(fileName):
    with open(fileName, 'w') as file:
        json.dump(queries, file)


def refresh():
    global queries

    for search in queries.items():
        for query_url in search[1]:
            run_query(query_url, search[0])

def send_mail(message):
    sender_address = ''
    password = ''

    receiver_address = ''

    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    server.login(sender_address,password)

    print('Login Success')
    print(message)
    server.sendmail(sender_address, receiver_address, msg=message)

    print('Email sent\n')


def run_query(query_url, query_name):
    global queries
    headers = { 'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:76.0) Gecko/20100101 Firefox/76.0 '}

    msg = ''
    page = requests.get(query_url, headers=headers)
    soup = BeautifulSoup(page.content, 'lxml')

    items = soup.find('div', {'class':'jsx-59941399 items visible'}).find_all('div',{'class':'jsx-3924372161 items__item'})

    for item in items:
        product_div = item.find(class_ = 'jsx-3924372161 item-key-data')

        title = product_div.find('h2').text #name of the insertion
        price_div = product_div.find('h6') #price of the product
        if price_div is None:
            price = None
        else:
            price = price_div.text

        location = product_div.find(class_ = 'classes_sbt-text-atom__2GBat classes_token-caption__1Ofu6 classes_size-small__3diir classes_weight-semibold__1RkLc classes_town__W-0Iq').string

        link = item.find(class_ = 'jsx-3924372161 link')['href']

        if price is not None:
            msg_text = f'New result for the search: {query_name} \nprice: {(price[:-1])}euro | location:{location} \nlink: {link}\n\n'
        else:
            msg_text = f'New result for the search: {query_name} \nprice: {price}euro | location:{location} \nlink: {link}\n\n'


        if queries.get(query_name) is None: #adding new query search and first item
            queries[query_name] = {query_url: {title: {'link': link, 'price': price, 'location':location}}}
            msg += msg_text
        else: #adding new query found element
            if queries[query_name][query_url].get(title) is None:
                queries[query_name][query_url][title] = {'link': link, 'price': price, 'location':location}
                msg += msg_text


    if len(msg) != 0:
        send_mail(str(msg))
    # else:
    #     print(f'\nAll lists for the search \"{query_name}\" are already up to date.\n')



load_file(dbFile)

while True:

    refresh()
    time.sleep(200)




save(dbFile)
