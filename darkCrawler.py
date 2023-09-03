#!/usr/bin/env python
import requests
from lxml import html
from urllib.parse import urljoin, urlparse
import collections
import sys
import re

# Disable SSL warnings
try:
    import requests.packages.urllib3
    requests.packages.urllib3.disable_warnings()
except ImportError:
    pass

# Define the starting .onion URL as a command-line argument
START = sys.argv[1]

# Set up a deque for URL queue
urlq = collections.deque()
urlq.append(START)

# Set to keep track of visited URLs
visited = set()

while urlq:
    url = urlq.popleft()

    try:
        response = requests.get(url, verify=False)  # Disable SSL verification for .onion domains
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching URL {url}: {e}")
        continue

    # Print the page title
    try:
        body = html.fromstring(response.content)
        page_title = body.xpath('//title/text()')
        print(f"Title: {page_title}")

        # Extract links from the page and add them to the queue
        links = body.xpath('//a/@href')
        for link in links:
            absolute_link = urljoin(url, link)
            if absolute_link not in visited:
                urlq.append(absolute_link)
                visited.add(absolute_link)

    except Exception as e:
        print(f"Error parsing page: {e}")

print("Crawling completed.")
