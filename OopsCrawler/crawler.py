import argparse
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import csv
from tqdm import tqdm
import sys
import re
import itertools
import threading
import time

ERROR_PHRASES = [
    '404 not found', 'page not found', 'error 404', '500 internal server error',
    'bad gateway', 'service unavailable', 'forbidden', 'access denied', 'site can’t be reached',
    'temporarily unavailable', 'not available', 'problem loading page', 'application error',
    # Social media and common soft-404 phrases
    "this content isn't available at the moment",
    "this account doesn’t exist",
    "hmm...this page doesn’t exist",
    "this page doesn’t exist",
    "hmm...this page doesn’t exist. try searching for something else",
    "sorry, this page isn't available.",
]

WHITELIST_DOMAINS = ['github.com']


def is_broken(status_code, content, url):
    if status_code >= 400:
        return True
    if status_code == 200:
        domain = urlparse(url).netloc
        if any(whitelisted in domain for whitelisted in WHITELIST_DOMAINS):
            return False
        content_lower = content.lower()
        for phrase in ERROR_PHRASES:
            if phrase in content_lower:
                return True
    return False


def get_all_links(start_url):
    visited = set()
    to_visit = set([start_url])
    all_links = set()
    domain = urlparse(start_url).netloc

    # Spinner animation setup
    spinner_running = True
    spinner_done = False
    def spinner():
        for c in itertools.cycle(['|', '/', '-', '\\']):
            if spinner_done:
                break
            print(f'\rCrawling links... {c}', end='', flush=True)
            time.sleep(0.1)
        print('\rCrawling links... done!   ')

    spinner_thread = threading.Thread(target=spinner)
    spinner_thread.start()

    while to_visit:
        url = to_visit.pop()
        if url in visited:
            continue
        visited.add(url)
        try:
            resp = requests.get(url, timeout=10)
            soup = BeautifulSoup(resp.text, 'html.parser')
            for a in soup.find_all('a', href=True):
                link = urljoin(url, a['href'])
                parsed = urlparse(link)
                if parsed.scheme.startswith('http'):
                    all_links.add(link)
                    # Only crawl links within the same domain
                    if parsed.netloc == domain and link not in visited:
                        to_visit.add(link)
        except Exception:
            continue
    spinner_done = True
    spinner_thread.join()
    return list(all_links)


def check_link(url):
    try:
        resp = requests.get(url, timeout=10, allow_redirects=True)
        final_url = resp.url
        status_code = resp.status_code
        if status_code == 999:
            print(f"Blocked by site: {url}")
            return url, final_url, status_code, '🚫 BLOCKED/UNKNOWN'
        broken = is_broken(status_code, resp.text, url)
        if broken:
            print(f"Broken: {url} (status: {status_code})")
            return url, final_url, status_code, '❌ BROKEN'
        return url, final_url, status_code, '✅ OK'
    except Exception as e:
        print(f"Exception for {url}: {e}")
        return url, '', 0, '❌ BROKEN'


def main():
    banner = r'''
 .d88888b.                              .d8888b.                                888                  
d88P" "Y88b                            d88P  Y88b                               888                  
888     888                            888    888                               888                  
888     888  .d88b.  88888b.  .d8888b  888        888d888 8888b.  888  888  888 888  .d88b.  888d888 
888     888 d88""88b 888 "88b 88K      888        888P"      "88b 888  888  888 888 d8P  Y8b 888P"   
888     888 888  888 888  888 "Y8888b. 888    888 888    .d888888 888  888  888 888 88888888 888     
Y88b. .d88P Y88..88P 888 d88P      X88 Y88b  d88P 888    888  888 Y88b 888 d88P 888 Y8b.     888     
 "Y88888P"   "Y88P"  88888P"   88888P'  "Y8888P"  888    "Y888888  "Y8888888P"  888  "Y8888  888     
                     888                                                                             
                     888                                                                             
                     888                                                                             
                                      made by lazy_sharaf
'''
    print(banner)
    parser = argparse.ArgumentParser(description='Crawl a site and check all anchor links.')
    parser.add_argument('start_url', nargs='?', help='The starting URL to crawl')
    parser.add_argument('--url-file', help='File containing a list of URLs to crawl (one per line)')
    parser.add_argument('--output', default='report.csv', help='CSV output file')
    args = parser.parse_args()

    # Gather URLs to process
    urls = []
    if args.url_file:
        try:
            with open(args.url_file, 'r', encoding='utf-8') as f:
                urls = [line.strip() for line in f if line.strip()]
        except Exception as e:
            print(f"Error reading URL file: {e}")
            return
    elif args.start_url:
        urls = [args.start_url]
    else:
        print("You must provide either a start_url or --url-file.")
        return

    all_broken_links = []
    for url in urls:
        print(f'\nCrawling site from: {url}')
        # Check if the site is accessible before crawling
        try:
            resp = requests.get(url, timeout=10)
            if resp.status_code >= 400:
                print(f"\n{'='*50}\n🚫 Site is not accessible at this moment (status code: {resp.status_code})\n{'='*50}\n")
                continue
        except Exception as e:
            print(f"\n{'='*50}\n🚫 Site is not accessible at this moment.\nReason: {e}\n{'='*50}\n")
            continue

        links = get_all_links(url)
        print(f'Found {len(links)} links. Checking...')
        results = []
        for link in tqdm(links, desc='Checking links', file=sys.stdout):
            results.append(check_link(link))
        # Only keep broken or blocked links, and add the source site for clarity
        for r in results:
            if r[3] in ['❌ BROKEN', '🚫 BLOCKED/UNKNOWN']:
                all_broken_links.append((url, *r))

    if all_broken_links:
        with open(args.output, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['Source Site', 'Original URL', 'Final URL', 'Status Code', 'Status'])
            writer.writerows(all_broken_links)
        print(f'Broken links report written to {args.output}')
    else:
        print('\n' + '='*50)
        print('🎉 No broken links found! 🎉'.center(50))
        print('='*50 + '\n')

if __name__ == '__main__':
    main() 