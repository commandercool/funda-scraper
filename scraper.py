from funda import Funda
from telegram_bot import TelegramBot
import os
import sys

MESSAGE_TEMPLATE = """
New apartment is out\.
The elevator is *%s*\.

Number of stories \- *%s*\.
Listing price \- *%s*\.

[check out on funda](%s)
"""
ENV_FUNDA_DB = 'FUNDA_DB'
ENV_TELEGRAM_TOKEN = 'TELEGRAM_TOKEN'
ENV_CHAT_ID = 'CHAT_ID'
ENV_SEARCH_URL = 'SEARCH_URL'

if ENV_FUNDA_DB not in os.environ or ENV_TELEGRAM_TOKEN not in os.environ \
    or ENV_CHAT_ID not in os.environ:
    print(f'ERROR: The following environment variables must be set: {ENV_FUNDA_DB}, {ENV_TELEGRAM_TOKEN}, {ENV_CHAT_ID} and {ENV_SEARCH_URL}',
           file=sys.stderr)
    exit(1)

sqlite_location = os.environ[ENV_FUNDA_DB]
telegram_token = os.environ[ENV_TELEGRAM_TOKEN]
chat_id = os.environ[ENV_CHAT_ID]
search_url = os.environ[ENV_SEARCH_URL]

funda = Funda(sqlite_location, search_url)
telegramBot = TelegramBot(chat_id, telegram_token)

newListing = funda.fetchNew()
for listing in newListing:
    print('scraper: sending message over telegram')
    telegramBot.postMessage(MESSAGE_TEMPLATE % 
        ('mentioned' if listing.hasElevator else 'not mentioned',
         listing.stories,
         listing.price.replace('.', '\\.'),
         listing.link))