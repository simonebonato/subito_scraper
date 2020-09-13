import requests
from bs4 import BeautifulSoup
import os.path
import json
import smtplib
import argparse

parser = argparse.ArgumentParser(description='Makes a query search in Subito.it')
parser.add_argument('--delete','-d',nargs='+',dest='delete', help='name of the search you want to delete')
parser.add_argument('--refresh','-r',dest='refresh',action='store_true', help ='refreshes the results of each saved search')

parser.add_argument('--list','-l',action='store_true', help ='shows a list of the current searches')
parser.add_argument('--print','-p',action='store_true', help ='prints all the current searches with the relative results')

parser.add_argument('--url', help='url of the new search you mean to make')
parser.add_argument('--name',nargs='+', help='name of the new search you mean to make')

parser.set_defaults(refresh=False, list=False, print = False)

args = parser.parse_args()

queries = dict()
dbFile = 'tracked_searches'


def load_file(fileName):
    global queries
    if not os.path.isfile(fileName):
        return
    with open(fileName) as file:
        queries = json.load(file)

def save(fileName):
    with open(fileName, 'w') as file:
        json.dump(queries, file)

def print_queries():
    global queries

    for search in queries.items():
        print('\nsearch:', search[0]) #prints the name of the wanted objet
        for query_url in search[1].items():
            print('query url:', query_url[0],'\n')
            for item in query_url[1].items():
                print ('title:', item[0])
                price = item[1].get('price')
                location = item[1].get('location')
                link = item[1].get('link')
                print(f'price: {price} | location: {location} \nlink: {link}\n')

def delete_query(query_name):
    global queries
    queries.pop(query_name)
    print(f'The search \"{query_name}\" has been deleted.')


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

def list():
    print('These are the current running queries:')
    for search in queries:
        print(f'-{search}')
    print()

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
    else:
        print(f'\nAll lists for the search \"{query_name}\" are already up to date.\n')



if __name__ == '__main__':
    load_file(dbFile)


if args.list:
    list()

if args.refresh:
    refresh()

if args.print:
    print_queries()

if args.delete is not None:
    delete_query(' '.join(args.delete))

if args.url is not None and args.name is not None:
    run_query(args.url, ' '.join(args.name))



save(dbFile)
