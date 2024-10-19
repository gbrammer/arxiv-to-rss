# arxiv-to-rss
Create an RSS feed from a custom arXiv query.

With the ``queries.yaml`` file as below, the files [feeds/feed.xml](https://gbrammer.github.io/arxiv-to-rss/feeds/feed.xml)
and [feeds/author.xml](https://gbrammer.github.io/arxiv-to-rss/feeds/author.xml) will be created.

Markdown versions of the paper summaries will also be parsed and pushed to the pages [feeds/feed.html](https://gbrammer.github.io/arxiv-to-rss/feeds/feed.html) and [feeds/author.html](https://gbrammer.github.io/arxiv-to-rss/feeds/author.html).

```yaml
feed:
  max_results: 64
  query: '(abs:JWST OR abs:James Webb) AND (cat:astro-ph.GA OR cat:astro-ph.CO)'

author:
  max_results: 64
  query: '(abs:JWST OR abs:James Webb) AND (cat:astro-ph.GA OR cat:astro-ph.CO) AND (au:Brammer)'
```

1. Edit ``queries.yaml`` to set the queries you want.  See the [API documentation](https://info.arxiv.org/help/api/user-manual.html#arxiv-api-users-manual) for more
   information on constructing queries.  Note that ``()`` will be changed to HTML characters and spaces to ``+`` in the query strings before sending them to the API.
1. Run `python queries_to_feeds.py` once locally and commit the ``xml`` and 
   ``md`` files it generates in the ``./feeds/`` subdirectory to the repo.
1. Enable **Read and write permissions** in ``Settings > Actions > General`` for the repository.
1. Turn on ``Settings > Pages`` to deploy to GitHub Pages from the ``main`` branch.
1. The feeds will be updated every weekday at 05:00 UT using the [GitHub Action](https://github.com/gbrammer/arxiv-to-rss/actions/workflows/update_feed.yml).
