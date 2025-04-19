import os

import feedparser
from dotenv import load_dotenv

load_dotenv()

RSS_URLS = os.getenv("RSS_URLS", "https://b.hatena.ne.jp/hotentry/it.rss")


class RSSService:
    def __init__(self):
        self.rss_urls = [url.strip() for url in RSS_URLS.split(",")]

    def list_rss_feed_entries(self):
        rss_entries = []
        for url in self.rss_urls:
            feed = feedparser.parse(url)
            rss_entries.extend(feed.entries)
        return rss_entries

    def get_rss_feed_urls(self):
        rss_entries = self.list_rss_feed_entries()
        return [entry["links"][0]["href"] for entry in rss_entries]
