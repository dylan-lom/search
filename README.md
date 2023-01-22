## Quickstart

```
sqlite3 search.db < create_database.sql
python3 -m pip install -r requirements.txt
python3 ./crawler.py
```

For development it is also recommended to install MyPy and type stubs:

```
python3 -m pip install mypy
python3 -m mypy --install-types
python3 -m mypy --strict .
```

## Keyword significance

Keyword occurances are assigned a value as described below and summed to get
the overall score of the keyword on the page:

```
Normal text (p, etc.): 1
Header text (h#): 7-# (ie. h3 = 4)
Page title (title): 7
```

When searching the page highest keyword score for the given query will be ranked
first

## References/Further Reading

1. [Kagi blog](https://blog.kagi.com/blog)
2. [The anatomy of a search engine](http://infolab.stanford.edu/pub/papers/google.pdf)

