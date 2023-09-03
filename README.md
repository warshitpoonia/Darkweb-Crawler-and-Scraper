
# Darkweb-Crawler-and-Scraper


Python-based Darkweb-Crawler-and-Scraper for beginners (basic modification on Scraper makes it a crawler)


Importing Libraries:

<pre>import requests
from lxml import html
from urllib.parse import urljoin, urlparse
import collections
import sys
import re</pre>

The code starts by importing necessary Python libraries. These libraries will be used for making HTTP requests, parsing HTML, working with URLs, managing a deque (double-ended queue), processing command-line arguments, and using regular expressions.

Disabling SSL Warnings (Optional):
<pre>try:
    import requests.packages.urllib3
    requests.packages.urllib3.disable_warnings()
except ImportError:
    pass</pre>
    
This section tries to disable SSL warnings using requests to suppress warnings related to SSL certificate verification. It is optional but can be helpful when dealing with .onion domains that often have self-signed certificates.

Setting the Starting URL:
<pre>START = sys.argv[1]</pre>

The script expects a .onion URL as a command-line argument and assigns it to the START variable.

Regular Expression for Email Addresses:
<pre>email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[a-z]{2,}\b'</pre>

This regular expression pattern matches and extracts email addresses from web pages. It looks for typical email address patterns.

Initializing Data Structures:
<pre>urlq = collections.deque()
urlq.append(START)
visited = set()
visited.add(START)
extracted_emails = []</pre>

Several data structures are initialized:
urlq: A deque (double-ended queue) to manage a queue of URLs to visit.
visited: A set to keep track of visited URLs to prevent revisiting them.
extracted_emails: A list to store the extracted email addresses.

Main Loop:
<pre>while urlq:</pre>

This loop continues as long as there are URLs in the queue to visit.

Fetching and Processing URLs:
<pre>url = urlq.popleft()
response = requests.get(url, verify=False)</pre>

It dequeues the next URL to visit and sends an HTTP GET request to that URL. The verify=False parameter disables SSL certificate verification to accommodate .onion domains with self-signed certificates.

Extracting Email Addresses:
<pre>email_matches = re.findall(email_pattern, response.text)
extracted_emails.extend(email_matches)</pre>

The script extracts email addresses from the web page's HTML content using the regular expression pattern. Extracted email addresses are added to the extracted_emails list.

Printing Page Title:
<pre>body = html.fromstring(response.content)
page_title = body.xpath('//title/text()')
print(page_title)</pre>

It parses the HTML content of the web page to extract the page title and prints it. The html.fromstring() function is used to parse the HTML content.

Filtering Links:
<pre>base_url = urlparse(url)
links = {urljoin(url, href) for href in body.xpath('//a/@href')}
links = {link for link in links if urlparse(link).netloc == base_url.netloc}</pre>

The script extracts all links (URLs) from the web page's HTML content and filters them to ensure they belong to the same domain as the current page.

Handling New URLs:
<pre>new_links = [link for link in links if link not in visited]
urlq.extend(new_links)
visited.update(new_links)</pre>

It filters out links that have not been visited yet and adds them to the queue (urlq) for future processing. Visited URLs are also tracked to prevent revisiting.

Writing Extracted Email Addresses to a File:
<pre>with open('extracted_emails.txt', 'w') as email_file:
    for email in extracted_emails:
        email_file.write(email + '\n')</pre>

Finally, the script writes the extracted email addresses to a text file named 'extracted_emails.txt'.
This code is designed to scrape email addresses from web pages of .onion domains, while also handling URLs within the same domain and keeping track of visited URLs. It provides better organization and error handling compared to the initial script.
