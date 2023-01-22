#!/usr/bin/env python3

import re
import sys
import sqlite3
from typing import Dict, List, Optional
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup

sites = [
	# 'http://dlom.cc',
	# 'http://dylanlom.com',
	# 'http://rss.dlom.cc',
	'https://docs.python.org/3/',
]

blocked_extensions = [ 'pdf', 'zip', 'tar', 'bz2', 'gz', 'exe', 'appimage', 'jpg', 'jpeg', 'png', 'epub' ]

db_con = sqlite3.connect('./search.db')
db = db_con.cursor()

KEYWORD_SCORES = {
	'h6': 1,
	'h5': 2,
	'h4': 3,
	'h3': 4,
	'h2': 5,
	'h1': 6,
	'title': 7,
}

def is_visited(site: str) -> bool:
	params = (site, )
	res = db.execute('SELECT `path` FROM `pages` WHERE `path` = ?', params)
	return res.fetchone() is not None

def extract_keywords(soup: BeautifulSoup) -> Dict[str, int]:
	keywords = {}
	for keyword in KEYWORD_SCORES.keys():
		for occurance in soup.find_all(keyword):
			for word in occurance.get_text().split():
				if word not in keywords: keywords[word] = 0
				keywords[word] += KEYWORD_SCORES[keyword]

	# TODO: This will incorrectly double-count all of the special tag occurances
	for word in soup.get_text().split():
		if word not in keywords: keywords[word] = 0
		keywords[word] += 1

	return keywords

def save_keyword(page_id: int, keyword: str, score: int) -> None:
	db.execute(
		'''
			INSERT OR REPLACE INTO `pages_keywords` (`page`, `keyword`, `score`)
			VALUES (?, ?, ?)
		''',
		(page_id, keyword, score, ))

def save_keywords(page_id: int, keywords: Dict[str, int]) -> None:
	for keyword, score in keywords.items():
		save_keyword(page_id, keyword, score)

def save_page(site: str, title: str) -> int:
	params = (site, title, )
	res = db.execute('INSERT INTO `pages` (`path`, `title`) VALUES (?, ?)', params)
	page_id = res.lastrowid
	assert(page_id is not None)
	return page_id

def save(site: str, title: str, keywords: Dict[str, int]) -> None:
	page_id = save_page(site, title)
	save_keywords(page_id, keywords)
	db_con.commit()

def contains_substring(needles: List[str], haystack: str) -> bool:
	for needle in needles:
		if needle in haystack: return True
	return False

def next_site(href: str, current: str) -> Optional[str]:
	next = urljoin(current, href)
	if next.split('.').pop().lower() in blocked_extensions: return None

	scheme, netloc, path, *_ = urlparse(next)
	next = f'{scheme}://{netloc}{path}'
	if scheme not in ['http', 'https']: return None
	if not contains_substring(sites, next): return None
	return next

def process(site: str) -> List[str]:
	resp = requests.get(site)
	if 'text/html' not in resp.headers['content-type']: return []
	soup = BeautifulSoup(resp.text, 'html.parser')

	# PEP 505 when? 🙃
	title = site # Fallback for when we don't get a title...
	if soup.head and soup.head.title and len(soup.head.title.contents):
		title = soup.head.title.contents[0].get_text()

	keywords = extract_keywords(soup)
	save(site, title, keywords)

	links = [ next_site(a.get('href'), site) for a in soup.find_all('a') ]
	return [ site for site in links if site ]

def crawl(sites: List[str], level: int = 0) -> None:
	if len(sites) == 0: return
	indent = ' ' * level
	links = []

	for site in sites:
		if is_visited(site): continue
		print(f'{indent} {site}')
		links += process(site)

	crawl(links, level + 1)

if __name__ == '__main__':
	crawl(sites)
	db_con.close()
