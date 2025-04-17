"""
Main application for AI News Slack Bot.
Coordinates RSS feeds, summarization, and Slack notifications.
"""
import time
import logging
import os
import sys
from dotenv import load_dotenv
from src.rss_reader import RSSReader
from src.ai_summarizer import AISummarizer, SimpleSummarizer  # Import both summarizer options
from src.slack_notifier import SlackNotifier

# Load environment variables
load_dotenv()

# Set up logging
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    handlers=[logging.StreamHandler(sys.stdout)])
logger = logging.getLogger('main')

class AINewsBot:
    def __init__(self, feed_urls=None, check_interval=3600, use_openai=True):
        """
        Initialize the AI News Bot.
        
        Args:
            feed_urls: List of RSS feed URLs to monitor
            check_interval: How often to check for new articles (in seconds)
            use_openai: Whether to use OpenAI for summarization or the simple summarizer
        """
        # Default AI news feed URLs if none provided
        self.feed_urls = feed_urls or [
            "https://blog.google/technology/ai/rss/",
            "https://www.technologyreview.com/topic/artificial-intelligence/feed",
            "https://openai.com/blog/rss.xml",
            "https://www.reddit.com/r/MachineLearning/.rss",
            "https://www.reddit.com/r/artificial/.rss"
        ]
        
        self.check_interval = check_interval
        
        # Initialize components
        self.rss_reader = RSSReader(self.feed_urls)
        
        # Choose summarizer based on parameter and API key availability
        if use_openai and os.getenv("OPENAI_API_KEY"):
            logger.info("Using OpenAI for summarization")
            self.summarizer = AISummarizer()
        else:
            logger.info("Using simple text summarizer")
            self.summarizer = SimpleSummarizer()
            
        self.slack_notifier = SlackNotifier()
        
        logger.info(f"AI News Bot initialized with {len(self.feed_urls)} feeds")
        
    def run_once(self):
        """
        Run the bot once to check for and process new articles.
        
        Returns:
            Number of articles posted to Slack
        """
        try:
            # 1. Get new articles from RSS feeds
            logger.info("Checking for new articles...")
            new_articles = self.rss_reader.get_new_articles()
            
            if not new_articles:
                logger.info("No new articles found")
                return 0
                
            logger.info(f"Found {len(new_articles)} new articles")
            
            # 2. Generate summaries
            logger.info("Generating summaries...")
            
            # Handle both summarizer types (they have the same method name)
            summarized_articles = self.summarizer.batch_summarize(new_articles)
            
            # 3. Post to Slack
            logger.info("Posting to Slack...")
            posted_count = self.slack_notifier.send_batch_notifications(summarized_articles)
            
            logger.info(f"Posted {posted_count} articles to Slack")
            return posted_count
            
        except Exception as e:
            logger.error(f"Error in run_once: {str(e)}")
            return 0
            
    def run_continuously(self):
        """
        Run the bot in a continuous loop, checking for new articles at the specified interval.
        """
        logger.info(f"Starting continuous mode, checking every {self.check_interval} seconds")
        
        try:
            while True:
                self.run_once()
                logger.info(f"Sleeping for {self.check_interval} seconds...")
                time.sleep(self.check_interval)
                
        except KeyboardInterrupt:
            logger.info("Bot stopped by user")
        except Exception as e:
            logger.error(f"Error in continuous mode: {str(e)}")

# Example usage
if __name__ == "__main__":
    # If SimpleSummarizer doesn't exist yet, create it by duplicating AISummarizer
    # and removing the OpenAI-specific code
    try:
        from src.ai_summarizer import SimpleSummarizer
    except ImportError:
        logger.warning("SimpleSummarizer not found. Make sure it's implemented in ai_summarizer.py")
    
    # Create and run the bot
    bot = AINewsBot()
    
    # Run once for testing
    bot.run_once()
    
    # For production, use:
    # bot.run_continuously()