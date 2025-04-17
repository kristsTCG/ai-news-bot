"""
Slack Notifier module for AI News Slack Bot.
Sends notifications about AI news articles to a Slack channel.
"""
import os
import logging
import sys
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Set up logging with console output
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    handlers=[logging.StreamHandler(sys.stdout)])
logger = logging.getLogger('slack_notifier')

class SlackNotifier:
    def __init__(self, token=None, channel=None):
        """
        Initialize with a Slack bot token and channel ID.
        
        Args:
            token: Slack bot token
            channel: Channel ID to post to
        """
        # Use provided token or get from environment variables
        self.token = token or os.getenv("SLACK_BOT_TOKEN")
        self.channel = channel or os.getenv("SLACK_CHANNEL_ID")
        
        # Debug logging
        print(f"Token present: {self.token is not None}")
        print(f"Channel present: {self.channel is not None}")
        if self.token:
            print(f"Token starts with: {self.token[:10]}...")
        if self.channel:
            print(f"Channel: {self.channel}")
        
        if not self.token:
            logger.warning("No Slack bot token provided. Notifications will not work.")
            self.client = None
        else:
            # Initialize the Slack client
            self.client = WebClient(token=self.token)
            logger.info(f"Slack Notifier initialized with token and channel: {self.channel}")
    
    def send_message(self, text):
        """
        Send a simple text message to the Slack channel.
        
        Args:
            text: Message text to send
            
        Returns:
            True if successful, False otherwise
        """
        if not self.client or not self.channel:
            logger.error("Cannot send message: Missing Slack token or channel ID")
            return False
        
        try:
            print(f"Attempting to send message to channel {self.channel}")
            response = self.client.chat_postMessage(
                channel=self.channel,
                text=text
            )
            logger.info(f"Message sent to channel {self.channel}")
            print("Message sent successfully!")
            return True
        except SlackApiError as e:
            logger.error(f"Error sending message: {e.response['error']}")
            print(f"ERROR: {str(e)}")
            return False
    
    def send_article_notification(self, article):
        """
        Send a nicely formatted notification about an article.
        
        Args:
            article: Article dictionary with title, link, summary, etc.
            
        Returns:
            True if successful, False otherwise
        """
        if not self.client or not self.channel:
            logger.error("Cannot send notification: Missing Slack token or channel ID")
            return False
        
        try:
            # Extract article info
            title = article.get('title', 'Untitled Article')
            link = article.get('link', '')
            source = article.get('source', 'Unknown Source')
            published = article.get('published', 'Unknown date')
            ai_summary = article.get('ai_summary', 'No summary available')
            
            # Format as a Slack message with blocks
            blocks = [
                {
                    "type": "header",
                    "text": {
                        "type": "plain_text",
                        "text": f"📰 {title}"
                    }
                },
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"*Source:* {source}\n*Published:* {published}\n\n{ai_summary}"
                    }
                },
                {
                    "type": "actions",
                    "elements": [
                        {
                            "type": "button",
                            "text": {
                                "type": "plain_text",
                                "text": "Read Full Article"
                            },
                            "url": link
                        }
                    ]
                },
                {
                    "type": "divider"
                }
            ]
            
            # Send the message
            print(f"Attempting to send article notification to channel {self.channel}")
            response = self.client.chat_postMessage(
                channel=self.channel,
                blocks=blocks,
                text=f"New AI Article: {title}"  # Fallback text
            )
            logger.info(f"Article notification sent to channel {self.channel}")
            print("Article notification sent successfully!")
            return True
        except SlackApiError as e:
            logger.error(f"Error sending article notification: {e.response['error']}")
            print(f"ERROR: {str(e)}")
            return False
            
    def send_batch_notifications(self, articles):
        """
        Send notifications for a batch of articles.
        
        Args:
            articles: List of article dictionaries
            
        Returns:
            Number of successfully sent notifications
        """
        success_count = 0
        
        for article in articles:
            if self.send_article_notification(article):
                success_count += 1
        
        logger.info(f"Sent {success_count} of {len(articles)} article notifications")
        return success_count

# Example usage
if __name__ == "__main__":
    # This requires a Slack bot token and channel ID in .env file
    print("Initializing Slack notifier...")
    notifier = SlackNotifier()
    
    # First send a simple message
    print("Sending a simple test message...")
    simple_success = notifier.send_message("Hello from AI News Slack Bot! This is a test message.")
    print(f"Simple message sent: {simple_success}")
    
    # Then try the formatted article
    print("Sending formatted article notification...")
    test_article = {
        'title': 'New AI Model Achieves Breakthrough in Natural Language Understanding',
        'summary': 'Researchers have developed a new language model that demonstrates ' +
                   'unprecedented capabilities in understanding and generating human language.',
        'ai_summary': 'Researchers have developed a revolutionary language model with unprecedented ' +
                       'capabilities in understanding and generating human language, showing significant ' +
                       'improvements on various benchmarks.',
        'link': 'https://example.com/article',
        'published': '2025-04-16',
        'source': 'AI Research Journal'
    }
    
    article_success = notifier.send_article_notification(test_article)
    print(f"Article notification sent: {article_success}")