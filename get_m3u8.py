import requests
import sys
import re
import time
import cloudscraper


def get_link(link: str) -> str:
    if "jable.tv" in link:
        htmlfile = cloudscraper.create_scraper().get(link)
        result = re.search("https://.+m3u8", htmlfile.text)
        m3u8url = result[0]
        return m3u8url
    else:
        return link


link = get_link(sys.argv[1])
print(link)
