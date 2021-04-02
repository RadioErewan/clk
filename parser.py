from rss_parser import Parser
from requests import get

rss_url = "https://tvn24.pl/najnowsze.xml"
xml = get(rss_url)

# Limit feed output to 5 items
# To disable limit simply do not provide the argument or use None
parser = Parser(xml=xml.content, limit=5)
feed = parser.parse()

# Print out feed meta data
print(feed.language)
print(feed.version)

# Iteratively print feed items
for item in feed.feed:
    print(item.title)
    print(item.description)