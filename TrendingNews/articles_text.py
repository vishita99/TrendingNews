"""
This script fetches the article texts from the news IDs
"""

from newspaper import Article
from newspaper import Config
import traceback
import time
import random

class ArticleText:
    def __init__(self, current_trendings_articles):
        """
        Initializes the ArticleText object with the provided dataset of current trending articles.
        
        Args:
            current_trendings_articles (pandas dataset): Contains list of today/current trending article IDs.
        """
        self.trending_articles_with_text = current_trendings_articles
        self.get_all_article_text()
           
    def get_all_article_text(self):
        """
        Iterates through all articles and extracts text from each article.
        """
        for count in range(0, len(self.trending_articles_with_text)):
            try:
                text = self.get_single_article_text(self.trending_articles_with_text[count]['stories'])

                #delete a story if text could not be fetched
                if text == '':
                    del self.trending_articles_with_text[count]
                    continue
                self.trending_articles_with_text[count]['article_text'] = text

                if count != (len(self.trending_articles_with_text)-1):
                    self.sleep_for_seconds()
            except Exception as e:
                traceback.print_exc()

    def get_single_article_text(self, article):
        """
        Extracts text from a single article.
        
        Args:
            article (dict): Information about the article- article title, ID, url, image.
        
        Returns:
            text (str): Extracted text from the article.
        """
        text = ''
        if article['url'] == '':
            return text
        try:
            user_agent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:78.0) Gecko/20100101 Firefox/78.0'
            config = Config()
            config.browser_user_agent = user_agent
            config.request_timeout = 25
            article_info = Article(article['url'].strip(), config=config)
            article_info.download()
            article_info.parse()
            text = article_info.text
        except:
            pass
        return text
    
    def sleep_for_seconds(self):
        """
        Sleeps for a random duration between 2 and 5 seconds.
        """
        time.sleep(random.randint(2, 5))
