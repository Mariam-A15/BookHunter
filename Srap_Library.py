import requests
from bs4 import BeautifulSoup
import sqlite3
from word2number import w2n
import os

script_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(script_dir)

response = requests.request('GET' , 'https://books.toscrape.com/')
soup = BeautifulSoup(response.text , 'html.parser')

connection = sqlite3.connect('Library.db')

for category in soup.find('div',attrs = {'class':'side_categories'}).find('ul').find('ul').find_all('li'):
    category_name = category.text.strip()
    category_link = 'https://books.toscrape.com/'+category.find('a').get('href')
    category_soup=BeautifulSoup(requests.request('GET',category_link).text,'html.parser')
    curser = connection.execute('insert into Categories (CatName) values (?)',[category_name])
    for item in category_soup.find('ol',attrs = {'class': 'row'}).find_all('li'):
        Book_name = item.find('h3').find('a').get('title')
        Book_price = item.find('p',attrs={'class':'price_color'}).text[2:]
        Book_rating=w2n.word_to_num(item.find('article').find('p').get('class')[-1])
        curser = connection.execute('insert into Books (BookName,BookPrice,BookRate,CatID) values (?,?,?,(select CatID from Categories where CatName =?))',[Book_name,Book_price,Book_rating,category_name])
    #check if there is a next page 
    next=category_soup.find('li',attrs = {'class':'next'})
    if next is not None:
        next_soup=category_soup
    #While loop to extract all the next pages
    while next is not None :
        next_link = category_link[:category_link.rfind('/')]+'/' + next_soup.find('li',attrs={'class':'next'}).find('a').get('href')
        next_soup = BeautifulSoup(requests.request('GET',next_link).text,'html.parser')
        for item in next_soup.find('ol',attrs = {'class': 'row'}).find_all('li'):
            Book_name = item.find('h3').text
            Book_price = item.find('p',attrs={'class':'price_color'}).text[2:]
            curser = connection.execute('insert into Books (BookName,BookPrice,BookRate,CatID) values (?,?,?,(select CatID from Categories where CatName =?))',[Book_name,Book_price,Book_rating,category_name])
        next=next_soup.find('li',attrs = {'class':'next'})

connection.commit()
connection.close()
