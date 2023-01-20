#!/usr/bin/env python3

import re
import sys
from urllib.parse import urljoin, urlparse
from pathlib import Path

import requests
from bs4 import BeautifulSoup

start = 'http://dlom.cc'
save_dir = Path('./sites')
visited = {}

MAX_DEPTH = 4

def save(site, content):
	m = re.compile('^https?:\/\/').match(site)
	path = save_dir.joinpath(site[m.end():])

	if not path.exists(): path.mkdir(parents=True)
	visited[site] = True

	path = path.joinpath('content.txt')
	path.write_text(content)
	return str(path)

def nextSite(href, current):
	next = urljoin(current, href)
	if next in visited: return None
	if next.split('.').pop().lower() in ['pdf']: return None

	scheme, netloc, *_ = urlparse(next)
	if scheme not in ['http', 'https']: return None
	if 'dlom.cc' not in netloc: return None
	return next

def process(site, level=0):
	if site is None: return
	indent = ' ' * level
	print(f'{indent} {site}')
	resp = requests.get(site)
	soup = BeautifulSoup(resp.text, 'html.parser')
	save(site, soup.get_text())
	for link in soup.find_all('a'):
		if level > MAX_DEPTH: continue
		href = link.get('href')
		process(nextSite(href, site), level + 1)



process(start)
