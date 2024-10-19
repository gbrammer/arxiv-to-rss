import os
import datetime
from time import mktime

import feedparser
import rfeed

API_URL = "http://export.arxiv.org/api/query?search_query="
API_QUERY = """(abs:JWST+OR+abs:James+Webb)
+AND+(cat:astro-ph.GA+OR+cat:astro-ph.CO)
&sortBy=submittedDate
"""

API_QUERY = API_QUERY.replace('\n','').strip()
API_QUERY = API_QUERY.replace('(', '%28').replace(')','%29')

count_query = feedparser.parse(API_URL + API_QUERY + "&max_results=10")
count = int(count_query["feed"]["opensearch_totalresults"])

# dates = np.array([item["published"] for item in query["items"]])
# np.where(dates > '2022-12')[0].max() from full query

START = 1346
START = count - 100

query = feedparser.parse(
    API_URL + API_QUERY
    + f"&start={START}&max_results=5000&sortBy=lastUpdatedDate&sortOrder=ascending"
)

def get_item_published(item):
    return item["published"]

query["items"].sort(key=get_item_published)

feed_items = []

print(f"""Query: {API_QUERY}
Found {len(query["items"])} items.
""")

for item in query["items"]:
    
    _id = os.path.basename(item["link"]).split('v')[0]
    
    title = f"<![CDATA[{item['title']}]]"
    authors = [auth['name'].replace("\n","") for auth in item["authors"]]
    abstract = item["summary"].replace("\n","")
    if "arxiv_comment" in item:
        comment = item["arxiv_comment"].replace("\n","")
    else:
        comment = ""

    pdf_url = item["link"].replace("/abs/", "/pdf/")
    
    description = f"""<![CDATA[
{', '.join(authors)}
<br>
{abstract}
<br>
Comments: {comment}
<br> PDF: <a href="{pdf_url}" /> {pdf_url} </a>
]]"""

    feed_item = rfeed.Item(
        title=item["title"].replace("\n",""),
        link=item["link"],
        description = description,
        author = item["authors"][0]["name"],
        guid = rfeed.Guid(item["link"]),
        # enclosure=rfeed.Enclosure(url=image,type="image/jpeg",length=0),
        pubDate=datetime.datetime.fromtimestamp(mktime(item["published_parsed"])),
    )
    
    feed_items.append(feed_item)
    
feed = rfeed.Feed(
    title="JWST arXiv Feed",
    description = "Custom arXiv Query of JWST articles",
    language="en-US",
    items=feed_items,
    lastBuildDate = datetime.datetime.now(),
    link="https://github.com/gbrammer/arxiv-to-rss",
)

with open('feed.xml','w') as fp:
    fp.write(feed.rss())
    
