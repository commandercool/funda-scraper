import sqlite3
from typing import List
from bs4 import BeautifulSoup, Tag
import requests

class Listing:
  def __init__(self, street: str, link: str, price: str, hasElevator: bool, stories: str):
    self.street = street.strip()
    self.link = link.strip()
    self.hasElevator = hasElevator
    self.price = price.strip()
    self.stories = stories.strip()

  def __str__(self) -> str:
     return self.street + ' : ' + str(self.hasElevator) + ' : ' + self.price


class Funda:

    user_agent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:122.0) Gecko/20100101 Firefox/122.0'

    def __init__(self, db_location, search_url) -> None:
       print('funda: init client')
       sqlite_connection = sqlite3.connect(db_location)
       self.cursor = sqlite_connection.cursor()
       self.search_url = search_url

    def fetchNew(self) -> List[Listing]:
        print('funda: doing search')
        searchResult = requests.get(self.search_url, 
            headers={'User-Agent': self.user_agent})
        
        parsed_html = BeautifulSoup(searchResult.text, features="html.parser")
        listings = parsed_html.select('div[data-test-id="search-result-item"]')
        newListings = [x for x in listings if "Nieuw" in x.text]

        result = []

        print('funda: going over listings')
        for newListing in newListings:
            title = newListing.select('h2')[0]
            street = title.text.strip()
            print('funda: checking listing: ' + street)
            data = self.cursor.execute('SELECT * from listing WHERE street = ?', (street,)).fetchall()
            if len(data) == 0:
                print('funda: the listing is a new one!')
                self.cursor.execute('INSERT INTO listing VALUES (?)', (street,))
                self.cursor.connection.commit()
                link = title.parent
                apartmentPage = requests.get(link.get('href'), headers={'User-Agent': self.user_agent})
                apartment_page_parsed = BeautifulSoup(apartmentPage.text, features="html.parser")
                listing = Listing(
                    street=title.text, 
                    link=link.get('href'), 
                    price=self.fetchPrice(newListing),
                    hasElevator=self.hasElevator(apartmentPage),
                    stories=self.fetchNumberOfStories(apartment_page_parsed)
                )
                result.append(listing)
            else:
               print('funda: listing is an old one ...')
        return result
    
    def hasElevator(self, apartmentPage) -> bool:
       return ('elevator' in apartmentPage.text) or ('lift' in apartmentPage.text) \
            or ('Elevator' in apartmentPage.text) or ('Lift' in apartmentPage.text)
    
    def fetchNumberOfStories(self, apartment_page_parsed: Tag) -> str:
       terms = apartment_page_parsed.find_all('dt')
       for term in terms:
          if term.text == 'Number of stories' or term.text == 'Aantal woonlagen':
             description = term.find_next_siblings("dd")[0]
             print('fetched: ' + description.text)
             if description:
                return description.text.strip()
       return ''
    
    def fetchPrice(self, listing) -> str:
       return listing.select('p[data-test-id=price-sale]')[0].text
