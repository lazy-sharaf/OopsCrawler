# OopsCrawler

[![GitHub Repo](https://img.shields.io/badge/GitHub-OopsCrawler-blue?logo=github)](https://github.com/lazy-sharaf/OopsCrawler)

OopsCrawler is a Python-based web crawler that scans a website (or a list of websites) for all anchor links and checks if they are broken, blocked, or working. It generates a CSV report of problematic links, helping you maintain healthy, accessible websites.

---

## Features
- Recursively crawls all internal links from a starting URL or a list of URLs
- Checks each link for HTTP errors and common error phrases
- Skips error phrase checks for whitelisted domains (e.g., GitHub)
- Animated spinner during crawling for better UX
- Only saves broken/blocked links in the CSV report
- Friendly messages if no broken links are found
- Handles inaccessible sites gracefully
- Combined CSV report for multiple sites

---

## Requirements
- Python 3.7+
- The following Python packages (see `OopsCrawler/requirements.txt`):
  - requests
  - beautifulsoup4
  - tqdm

---

## Installation

### 1. Clone the repository
```sh
git clone https://github.com/lazy-sharaf/OopsCrawler.git
cd OopsCrawler
```

### 2. (Recommended) Create and activate a virtual environment
```sh
python -m venv venv
# For fish shell:
source venv/bin/activate.fish
# For bash/zsh:
source venv/bin/activate
```

### 3. Install dependencies
```sh
pip install -r OopsCrawler/requirements.txt
```

#### (Alternative) Install requirements with pacman (for Arch/CachyOS)
```sh
sudo pacman -S python-requests python-beautifulsoup4 python-tqdm
```

---

## Usage

### Check a single site
```sh
python OopsCrawler/crawler.py https://example.com
```

### Check a list of sites
1. Create a file (e.g., `urls.txt`) with one URL per line:
   ```
   https://example.com
   https://another-site.com
   ...
   ```
2. Run:
   ```sh
   python OopsCrawler/crawler.py --url-file urls.txt
   ```

### Specify a custom output file
```sh
python OopsCrawler/crawler.py https://example.com --output myreport.csv
python OopsCrawler/crawler.py --url-file urls.txt --output myreport.csv
```

---

## What happens?
- The script shows an animated spinner while crawling links.
- It checks each link and only saves broken/blocked links in the CSV report.
- If no broken links are found, you'll see a celebratory message and no CSV is written.
- If a site is inaccessible, you'll get a clear error message and the script will continue with the next site (if using a list).

---

## Example Output

**CSV columns:**
- Source Site
- Original URL
- Final URL
- Status Code
- Status (❌ BROKEN, 🚫 BLOCKED/UNKNOWN)

---

## Contribution
Pull requests and suggestions are welcome! Please open an issue or PR if you have improvements or bugfixes.

---

## License
MIT License

---

**Made by lazy_sharaf** 
