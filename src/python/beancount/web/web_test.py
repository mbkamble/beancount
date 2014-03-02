import time
import unittest
from os import path
import os
import re
import threading

import requests
import bs4
import lxml.html

from beancount.web import web


def find_repository_root():
    """Return the path to the repository root.

    Returns:
      A string, the root directory.
    """
    filename = __file__
    while not path.exists(path.join(filename, 'README')):
        filename = path.dirname(filename)
    return filename


def start_server(filename, port):
    thread = threading.Thread(
        target=web.run_app,
        args=(filename, port, False, False, False))
    thread.daemon = True # Automatically exit if the process comes dwn.
    thread.start()

    # Ensure the server has at least started before running the scraper.
    web.wait_ready()
    time.sleep(0.1)

    return thread


def shutdown_server(thread):
    # Clean shutdown: request to stop, then join the thread.
    # Note that because we daemonize, we could forego this elegant detail.
    web.shutdown()
    thread.join()


def scrape_urls(url_format, predicate, ignore_regexp=None):
    # The set of all URLs processed
    done = set()

    # The list of all URLs to process. We use a list here so we have
    # reproducible order if we repeat the test.
    process = ["/"]

    # Loop over all URLs remaining to process.
    while process:
        url = process.pop()

        # Mark as fetched.
        assert url not in done
        done.add(url)

        # Fetch the URL and check its return status.
        response = requests.get(url_format.format(url))
        predicate(response, url)

        # Skip served documents.
        if ignore_regexp and re.match(ignore_regexp, url):
            continue

        # Get all the links in the page and add all the ones we haven't yet
        # seen.
        for url in find_links(response.text):
            if url in done or url in process:
                continue
            process.append(url)


def find_links(html_text):
    root = lxml.html.fromstring(html_text)
    for a in root.xpath('//a'):
        assert 'href' in a.attrib
        yield a.attrib['href']


def scrape(filename, predicate, port=9468):
    url_format = 'http://localhost:{}{{}}'.format(port)
    thread = start_server(filename, port)
    scrape_urls(url_format, predicate, '^/doc/')
    shutdown_server(thread)


class TestWeb(unittest.TestCase):

    def check_page_okay(self, response, url):
        self.assertEqual(200, response.status_code, url)

    def test_scrape_basic(self):
        filename = path.join(find_repository_root(),
                             'examples', 'basic', 'basic.beancount')
        scrape(filename, self.check_page_okay, 9468)

    def test_scrape_starterkit(self):
        filename = path.join(find_repository_root(),
                             'examples', 'starterkit', 'starter.beancount')
        scrape(filename, self.check_page_okay, 9469)

    def test_scrape_thisisreal(self):
        filename = path.join(os.environ['HOME'],
                             'r/q/office/accounting/blais.beancount')
        if path.exists(filename):
            scrape(filename, self.check_page_okay, 9470)