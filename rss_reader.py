"""
RSS Reader module for AI News Slack Bot.
Fetches and parses RSS feeds from various AI news sources.
"""
import feedparser
import time
from datetime import datetime, timedelta
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('rss_reader')

class RSSReader:
    def __init__(self, feed_urls=None):
        """Initialize with a list of RSS feed URLs."""
        self.feed_urls = feed_urls or []
        logger.info(f"Initialized RSS Reader with {len(self.feed_urls)} feeds")
        
        # Store the last check time for each feed
        self.last_check = {}
        for url in self.feed_urls:
            self.last_check[url] = datetime.now() - timedelta(days=1)  # Start with fetching 1 day of news
    
    def add_feed(self, url):
        """Add a new RSS feed URL to monitor."""
        if url not in self.feed_urls:
            self.feed_urls.append(url)
            self.last_check[url] = datetime.now() - timedelta(days=1)
            logger.info(f"Added new feed: {url}")
        else:
            logger.info(f"Feed already exists: {url}")
    
    def remove_feed(self, url):
        """Remove an RSS feed URL from monitoring."""
        if url in self.feed_urls:
            self.feed_urls.remove(url)
            if url in self.last_check:
                del self.last_check[url]
            logger.info(f"Removed feed: {url}")
        else:
            logger.warning(f"Attempted to remove non-existent feed: {url}")
    
    def get_new_articles(self):
        """
        Fetch all feeds and return new articles since the last check.
        Returns a list of dictionaries with article information.
        """
        all_new_articles = []
        
        for url in self.feed_urls:
            try:
                logger.info(f"Fetching feed: {url}")
                feed = feedparser.parse(url)
                
                # Check for feed parsing errors
                if hasattr(feed, 'bozo_exception'):
                    logger.error(f"Error parsing feed {url}: {feed.bozo_exception}")
                    continue
                
                # Process each entry in the feed
                for entry in feed.entries:
                    # Parse the published date
                    published_time = None
                    if hasattr(entry, 'published_parsed'):
                        published_time = datetime.fromtimestamp(time.mktime(entry.published_parsed))
                    elif hasattr(entry, 'updated_parsed'):
                        published_time = datetime.fromtimestamp(time.mktime(entry.updated_parsed))
                    else:
                        # If no date is available, use current time
                        published_time = datetime.now()
                    
                    # Check if this is a new article
                    if published_time > self.last_check[url]:
                        # Extract article details
                        article = {
                            'title': entry.title,
                            'link': entry.link,
                            'published': published_time,
                            'source': feed.feed.title if hasattr(feed.feed, 'title') else 'Unknown',
                            'summary': entry.summary if hasattr(entry, 'summary') else '',
                            'content': entry.content[0].value if hasattr(entry, 'content') else ''
                        }
                        
                        all_new_articles.append(article)
                
                # Update the last check time for this feed
                self.last_check[url] = datetime.now()
                
            except Exception as e:
                logger.error(f"Error processing feed {url}: {str(e)}")
        
        logger.info(f"Found {len(all_new_articles)} new articles")
        return all_new_articles

# Example usage
if __name__ == "__main__":
    # Test with some AI news feeds
    ai_feeds = [
        "https://blog.google/technology/ai/rss/",
        "https://news.mit.edu/topic/artificial-intelligence2-rss.xml",
        "https://www.technologyreview.com/topic/artificial-intelligence/feed"
    ]
    
    reader = RSSReader(ai_feeds)
    articles = reader.get_new_articles()
    
    print(f"Found {len(articles)} new articles:")
    for article in articles:
        print(f"- {article['title']} ({article['published']}) - {article['link']}")