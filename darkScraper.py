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

# Regular expression pattern to match email addresses
email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[a-z]{2,}\b'

# Set up a deque for URL queue
urlq = collections.deque()
urlq.append(START)

# Set to keep track of visited URLs
visited = set()
visited.add(START)

# Create a list to store extracted email addresses
extracted_emails = []

while urlq:
    url = urlq.popleft()

    try:
        response = requests.get(url, verify=False)  # Disable SSL verification for .onion domains
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching URL {url}: {e}")
        continue

    # Extract email addresses from the page and add them to the list
    email_matches = re.findall(email_pattern, response.text)
    extracted_emails.extend(email_matches)

    # Print the page title
    try:
        body = html.fromstring(response.content)
        page_title = body.xpath('//title/text()')
        print(page_title)
    except Exception as e:
        print(f"Error parsing page title: {e}")

    # Find all links, making sure to stay on the same .onion site
    base_url = urlparse(url)
    links = {urljoin(url, href) for href in body.xpath('//a/@href')}
    links = {link for link in links if urlparse(link).netloc == base_url.netloc}

    # Filter out already visited URLs
    new_links = [link for link in links if link not in visited]

    # Add new URLs to the queue and mark them as visited
    urlq.extend(new_links)
    visited.update(new_links)

# Write extracted email addresses to a file
with open('extracted_emails.txt', 'w') as email_file:
    for email in extracted_emails:
        email_file.write(email + '\n')
