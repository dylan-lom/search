#!/usr/bin/env python3

import sys
import sqlite3
from urllib.parse import urlparse
from typing import Dict, List, Tuple

db_con = sqlite3.connect('./search.db')
db = db_con.cursor()

def search(query: str) -> List[Tuple[str, str]]:
	pages: Dict[int, int] = {}
	for word in query.split():
		params = (word.lower(), )
		res = db.execute(
			"""
				SELECT `page`, `score`
				FROM `pages_keywords`
				WHERE LOWER(`keyword`) = ?
			""",
			params)

		for page, score in res.fetchall():
			if page not in pages: pages[page] = 0
			pages[page] += score

	ranked_pages = list(pages.items())
	ranked_pages.sort(key=lambda x: x[1], reverse=True)

	results = []
	for page, _ in ranked_pages:
		params = (page, )
		res = db.execute('SELECT `path`, `title` FROM `pages` WHERE `id` = ?', params)
		results.append(res.fetchone())

	return results

def htmlize(results: List[Tuple[str, str]]) -> str:
	head = """
		<!DOCTYPE html>
		<html lang="en">
		<head>
			<title>Search results</title>
			<link rel="stylesheet" link="style.css" />
		</head>
		<body>
			<ol>
	"""

	core = [ f'<li><a href="{path}">{title}</a></li>' for path, title in results ]

	tail = """
			</ol>
		</body>
		</html>
	"""

	return head + '\n'.join(core) + tail

def display(results: List[Tuple[str, str]]) -> None:
	for i, result in enumerate(results):
		path, title = result
		print(f'{i+1}. {title} ({path})')

query = " ".join(sys.argv[1:])
if query == "": query = 'code'

results = search(query)
# display(results)
print(htmlize(results))

