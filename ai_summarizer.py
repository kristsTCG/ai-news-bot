"""
AI Summarizer module for AI News Slack Bot.
Provides two summarization options:
1. AISummarizer - Uses OpenAI's API for advanced AI-powered summarization
2. SimpleSummarizer - Uses text extraction techniques for basic summarization
"""
import os
import logging
import re
import openai
from collections import Counter
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Set up logging
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('ai_summarizer')

class AISummarizer:
    def __init__(self, api_key=None):
        """Initialize with an OpenAI API key."""
        # Use provided API key or get from environment variables
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        
        if not self.api_key:
            logger.warning("No OpenAI API key provided. Summarization will not work.")
        else:
            # Set the API key
            openai.api_key = self.api_key
            logger.info("AI Summarizer initialized with API key")
    
    def summarize_article(self, article):
        """
        Generate a concise summary of an article.
        
        Args:
            article: A dictionary containing article data including 
                    'title', 'content' or 'summary', and 'link'
        
        Returns:
            A string containing the generated summary or None if there was an error
        """
        if not self.api_key:
            logger.error("Cannot summarize: No OpenAI API key provided")
            return None
        
        try:
            # Prepare content for summarization
            title = article.get('title', 'Untitled Article')
            
            # Try to use full content if available, otherwise use summary
            text_to_summarize = article.get('content', article.get('summary', ''))
            if not text_to_summarize:
                logger.warning(f"No content to summarize for article: {title}")
                return f"No content available to summarize for {title}"
            
            # Prepare prompt for the AI
            prompt = f"""
            Please create a concise 2-3 sentence summary of this AI-related article.
            Focus on the key innovations, findings, or announcements.
            
            Title: {title}
            Content: {text_to_summarize}
            """
            
            # Call OpenAI API (compatible with version 0.28.0)
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a helpful assistant that summarizes AI news articles concisely."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=150,
                temperature=0.3
            )
            
            # Extract and return the summary
            summary = response['choices'][0]['message']['content'].strip()
            logger.info(f"Successfully summarized article: {title}")
            return summary
            
        except Exception as e:
            logger.error(f"Error summarizing article: {str(e)}")
            return f"Error summarizing article: {str(e)}"
            
    def batch_summarize(self, articles):
        """
        Summarize a batch of articles.
        
        Args:
            articles: A list of article dictionaries
            
        Returns:
            A list of dictionaries with original article data plus summaries
        """
        summarized_articles = []
        
        for article in articles:
            # Make a copy of the article data
            article_with_summary = article.copy()
            
            # Add AI-generated summary
            summary = self.summarize_article(article)
            article_with_summary['ai_summary'] = summary
            
            summarized_articles.append(article_with_summary)
            
        logger.info(f"Summarized {len(summarized_articles)} articles with AI")
        return summarized_articles

class SimpleSummarizer:
    def __init__(self):
        """Initialize the summarizer."""
        logger.info("Simple text summarizer initialized")
    
    def _extract_sentences(self, text):
        """Split text into sentences."""
        # Simple sentence splitter (not perfect but works for basic text)
        sentences = re.split(r'(?<!\w\.\w.)(?<![A-Z][a-z]\.)(?<=\.|\?|\!)\s', text)
        return [s.strip() for s in sentences if s.strip()]
    
    def _score_sentences(self, sentences):
        """Score sentences based on word frequency."""
        # Count word occurrences
        word_freq = Counter()
        for sentence in sentences:
            # Remove special characters and convert to lowercase
            cleaned = re.sub(r'[^\w\s]', '', sentence.lower())
            words = cleaned.split()
            word_freq.update(words)
        
        # Score each sentence
        scores = {}
        for i, sentence in enumerate(sentences):
            cleaned = re.sub(r'[^\w\s]', '', sentence.lower())
            words = cleaned.split()
            score = sum(word_freq[word] for word in words) / max(1, len(words))
            scores[i] = score
        
        return scores
    
    def summarize_article(self, article):
        """
        Generate a simple extractive summary of an article.
        
        Args:
            article: A dictionary containing article data
            
        Returns:
            A string containing a simple summary
        """
        try:
            # Get title and content
            title = article.get('title', 'Untitled Article')
            
            # Try to use full content if available, otherwise use summary
            text_to_summarize = article.get('content', article.get('summary', ''))
            if not text_to_summarize:
                logger.warning(f"No content to summarize for article: {title}")
                return f"No content available to summarize for {title}"
            
            # Extract sentences
            sentences = self._extract_sentences(text_to_summarize)
            if len(sentences) <= 2:
                # If there are only 1-2 sentences, just return them
                return text_to_summarize
            
            # Score sentences
            scores = self._score_sentences(sentences)
            
            # Select top 2-3 sentences
            num_sentences = min(3, max(2, len(sentences) // 5))
            top_indices = sorted(scores, key=scores.get, reverse=True)[:num_sentences]
            top_indices.sort()  # Sort by position in original text
            
            # Create summary
            summary = ' '.join([sentences[i] for i in top_indices])
            
            logger.info(f"Successfully summarized article: {title}")
            return summary
            
        except Exception as e:
            logger.error(f"Error summarizing article: {str(e)}")
            return f"Error summarizing: {str(e)}"
    
    def batch_summarize(self, articles):
        """
        Summarize a batch of articles.
        
        Args:
            articles: A list of article dictionaries
            
        Returns:
            A list of dictionaries with original article data plus summaries
        """
        summarized_articles = []
        
        for article in articles:
            # Make a copy of the article data
            article_with_summary = article.copy()
            
            # Add simple extractive summary
            summary = self.summarize_article(article)
            article_with_summary['ai_summary'] = summary
            
            summarized_articles.append(article_with_summary)
            
        logger.info(f"Summarized {len(summarized_articles)} articles with text extraction")
        return summarized_articles

# Example usage
if __name__ == "__main__":
    # Test both summarizers
    test_article = {
        'title': 'New AI Model Achieves Breakthrough in Natural Language Understanding',
        'summary': 'Researchers have developed a new language model that demonstrates ' +
                  'unprecedented capabilities in understanding and generating human language. ' +
                  'The model shows improved performance on a variety of benchmarks. ' +
                  'It uses a novel architecture that combines transformer-based processing ' +
                  'with memory-efficient attention mechanisms. The researchers claim it ' +
                  'requires significantly less computational resources than comparable models. ' +
                  'This could make advanced AI more accessible to smaller organizations. ' +
                  'Evaluation on standard NLP tasks shows a 15% improvement over previous models.',
        'link': 'https://example.com/article',
        'published': '2025-04-16',
        'source': 'AI Research Journal'
    }
    
    # First try the simple summarizer
    print("Testing SimpleSummarizer:")
    simple_summarizer = SimpleSummarizer()
    simple_summary = simple_summarizer.summarize_article(test_article)
    print(f"Simple Summary: {simple_summary}")
    
    # Then try the AI summarizer if an API key is available
    if os.getenv("OPENAI_API_KEY"):
        print("\nTesting AISummarizer:")
        ai_summarizer = AISummarizer()
        ai_summary = ai_summarizer.summarize_article(test_article)
        print(f"AI Summary: {ai_summary}")
    else:
        print("\nSkipping AISummarizer test (no API key available)")