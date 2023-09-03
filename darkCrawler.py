#!/usr/bin/env python
import sys
import sqlite3
from stem import process
from stem import Signal
from stem.control import Controller
from requests_socks import Session
from bs4 import BeautifulSoup
import scrapy

# Function to renew Tor identity (get a new IP)
def renew_tor_identity():
    with Controller.from_port(port=9051) as controller:
        controller.authenticate()
        controller.signal(Signal.NEWNYM)

# Disable SSL warnings
try:
    import requests.packages.urllib3
    requests.packages.urllib3.disable_warnings()
except ImportError:
    pass

# Define the starting .onion URL as a command-line argument
START = sys.argv[1]

# Set to keep track of visited URLs
visited = set()

# Initialize the SQLite database
conn = sqlite3.connect('crawler_database.db')
cursor = conn.cursor()

# Create a table to store crawled data
cursor.execute('''
    CREATE TABLE IF NOT EXISTS pages (
        id INTEGER PRIMARY KEY,
        url TEXT UNIQUE,
        title TEXT
    )
''')
conn.commit()

# Start the Tor process
with process.launch_tor_with_config(
        config = {
            'SocksPort': '9050',  # Configure Tor to listen on port 9050 for SOCKS proxy
            'ControlPort': '9051',  # Configure Tor to listen on port 9051 for control connection
            'DataDirectory': '/tmp/tor_data'  # Optional: Specify the data directory
        },
        init_msg_handler = print,
) as tor_process:
    # Renew Tor identity to get a new IP address
    renew_tor_identity()

    class MySpider(scrapy.Spider):
        name = 'my_spider'
        start_urls = [START]

        def parse(self, response):
            url = response.url
            visited.add(url)

            try:
                # Parse HTML content with BeautifulSoup4
                soup = BeautifulSoup(response.body, 'html.parser')
                page_title = soup.find('title').get_text()
                print(f"Title: {page_title}")

                # Store the visited URL and page title in the database
                cursor.execute('INSERT OR IGNORE INTO pages (url, title) VALUES (?, ?)', (url, page_title))
                conn.commit()

                # Extract links from the page and add them to the queue
                links = [urljoin(url, href) for href in soup.find_all('a', href=True)]
                for link in links:
                    if link not in visited:
                        yield response.follow(link, callback=self.parse)

            except Exception as e:
                print(f"Error parsing page: {e}")

    # Crawl using Scrapy
    process = scrapy.crawler.CrawlerProcess({
        'USER_AGENT': 'Mozilla/5.0',
        'LOG_ENABLED': False,
    })
    process.crawl(MySpider)
    process.start()

    # Close the database connection
    conn.close()

    # Stop the Tor process
    tor_process.terminate()

print("Crawling completed.")
