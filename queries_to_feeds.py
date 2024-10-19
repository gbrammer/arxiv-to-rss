import os
import datetime
from time import mktime, ctime

import yaml
import feedparser
import rfeed

API_URL = "http://export.arxiv.org/api/query?sortBy=lastUpdatedDate&search_query="
API_QUERY = """(abs:JWST+OR+abs:James+Webb)
+AND+(cat:astro-ph.GA+OR+cat:astro-ph.CO)
"""

with open("queries.yaml") as fp:
    query_specification = yaml.load(fp, Loader=yaml.Loader)

with open("queries_to_feeds.log.txt", "a") as fp:
    fp.write(f"\n######## {ctime()} ########\n")
    
for q in query_specification:
    
    qdata = query_specification[q]
    API_QUERY = qdata["query"].replace(" ", "+")
    API_QUERY = API_QUERY.replace('\n','').strip()
    API_QUERY = API_QUERY.replace('(', '%28').replace(')','%29')
    
    count_query = feedparser.parse(API_URL + API_QUERY + "&max_results=10")
    count = int(count_query["feed"]["opensearch_totalresults"])

    # dates = np.array([item["published"] for item in query["items"]])
    # np.where(dates > '2022-12')[0].max() from full query

    # START = 1346
    max_results = qdata["max_results"] if "max_results" in qdata else 100
    START = count - max_results

    query = feedparser.parse(
        API_URL + API_QUERY
        + f"&start={START}&max_results=5000&sortOrder=ascending"
    )

    def get_item_published(item):
        return item["published"]

    query["items"].sort(key=get_item_published, reverse=True)

    feed_items = []

    msg = f"""Query: feeds/{q}.xml {API_QUERY}
       Found {len(query["items"])} items (max={count}).\n"""
    with open("queries_to_feeds.log.txt", "a") as fp:
        fp.write(msg)
    
    print(msg)
    
    with open(f"feeds/{q}.md","w") as fp:
        fp.write(f"## {q} : \"{query_specification[q]['query']}\" N={max_results}\n")
        fp.write(f"### Updated {ctime()}\n\n")

    for i, item in enumerate(query["items"]):
    
        _id = os.path.basename(item["link"]).split('v')[0]
    
        title = f"{item['title']}".replace("\n"," ")
        authors = [auth['name'].replace("\n"," ") for auth in item["authors"]]
        abstract = item["summary"].replace("\n"," ")
        if "arxiv_comment" in item:
            comment = item["arxiv_comment"].replace("\n"," ")
        else:
            comment = ""

        pdf_url = item["link"].replace("/abs/", "/pdf/")
    
        description = f"""
<p> {', '.join(authors)} </p>
<p>
{abstract}
</p>
<p> Comments: {comment} </p>
<p> PDF: <a href="{pdf_url}"> {pdf_url} </a> </p>

"""

        with open(f"feeds/{q}.md","a") as fp:
            fp.write(f"### {i+1}) [{_id}]({item['link']}): {title}\n")
            fp.write(description)

        feed_item = rfeed.Item(
            title=item["title"].replace("\n"," "),
            link=item["link"],
            description = description,
            author = item["authors"][0]["name"],
            guid = rfeed.Guid(item["link"]),
            # enclosure=rfeed.Enclosure(url=image,type="image/jpeg",length=0),
            pubDate=datetime.datetime.fromtimestamp(mktime(item["published_parsed"])),
        )
    
        feed_items.append(feed_item)
    
    feed = rfeed.Feed(
        title=f"JWST arXiv Feed ({q})",
        description = "Custom arXiv Query of JWST articles",
        language="en-US",
        items=feed_items,
        lastBuildDate = datetime.datetime.now(),
        link="https://github.com/gbrammer/arxiv-to-rss",
    )

    with open(f'feeds/{q}.xml','w') as fp:
        fp.write(feed.rss())
    
