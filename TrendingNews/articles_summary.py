"""
This script generates a summary for each article text
"""

import re
import requests
import traceback
import os
import time
from dotenv import load_dotenv
load_dotenv()

#get the API of Pegasus huggingface model
API_URL = os.getenv("API_pegasus")
headers = {"Authorization": "Bearer {}".format(os.getenv("pegasus_authorisation_key"))}

class ArticleSummary:
    def __init__(self, current_trending_articles):
        """
        Initializes the ArticleSummary object with the provided dataframe of current trending articles
        
        Args:
            current_trending_articles (pandas df): Dataframe containing list of current trending articles
        """
        self.trending_articles_with_summary = current_trending_articles
        self.get_all_article_summary()
    
    def get_all_article_summary(self):
        """
        Iterates through all articles and generates summaries for each
        """
        for i in range(len(self.trending_articles_with_summary)):
            try:
                art_summ = self.text_summary_PEGASUS(self.trending_articles_with_summary[i]['article_text'])
                
                # drop the story if summary could not be generated
                if len(art_summ) > 0:
                    self.trending_articles_with_summary[i]['article_summary'] = art_summ
                else:
                    self.trending_articles_with_summary.drop(i, inplace=True)
            except Exception as e:
                traceback.print_exc()
  
    def query(self, payload):
        """
        Calls Pegasus API with the provided payload and returns the JSON response, i.e summary.
        
        Args:
            payload (dict): Payload for the POST request
        
        Returns:
            dict: JSON response from the API
        """
        response = requests.post(API_URL, headers=headers, json=payload)
        return response.json()
  
    def call_query(self, payloads):
        """
        Recursively calls the Pegasus model API by calling 'query' function until a successful response is received, handling errors and delays.
        
        Args:
            payloads (dict): Payloads for the POST request
        
        Returns:
            sub_article_summary (dict): JSON response from the API
        """
        sub_article_summary = self.query(payloads)
        if 'error' in sub_article_summary and 'estimated_time' in sub_article_summary:
            time.sleep(int(sub_article_summary['estimated_time']) + 5)
            return self.call_query(payloads)
        return sub_article_summary
              
    def text_summary_PEGASUS(self, article_text_raw):
        """
        Generates a summary for the given article text using the Pegasus API
        
        Args:
            article_text_raw (str): Raw article text
        
        Returns:
            final_summary (str): Generated summary for the article
        """
        summary = []
        article_text = self.remove_emojis(article_text_raw)
        if len(article_text.split(" ")) <= 60:
            return article_text  # if article has less than 60 words, return as is
        elif len(article_text.split(" ")) > 1000:
            j = 0
            while j + 1000 < len(article_text):
                sub_article_sum = self.call_query({"inputs": article_text[j:j+1000]})
                if sub_article_sum[0]['summary_text'] is not None:
                    summary.append(sub_article_sum[0]['summary_text'])
                j += 1000
            final_summary = ' '.join(summary)
            final_summary = final_summary.replace("<n>", "")
            return final_summary
        article_sum = self.call_query({"inputs": article_text})
        final_summary = article_sum[0]['summary_text'].replace("<n>", "")
        return final_summary

    def remove_emojis(self, text):
        """
        Removes emojis from the given text.
        
        Args:
            text (str): Input text.
        
        Returns:
            (str) : Cleaned text with emojis removed.
        """
        data = text.replace("\n\n", " ")
        emoj = re.compile("["
                          u"\U0001F600-\U0001F64F"  # emoticons
                          u"\U0001F300-\U0001F5FF"  # symbols & pictographs
                          u"\U0001F680-\U0001F6FF"  # transport & map symbols
                          u"\U0001F1E0-\U0001F1FF"  # flags (iOS)
                          u"\U00002500-\U00002BEF"  # chinese char
                          u"\U00002702-\U000027B0"
                          u"\U00002702-\U000027B0"
                          u"\U000024C2-\U0001F251"
                          u"\U0001f926-\U0001f937"
                          u"\U00010000-\U0010ffff"
                          u"\u2640-\u2642"
                          u"\u2600-\u2B55"
                          u"\u200d"
                          u"\u23cf"
                          u"\u23e9"
                          u"\u231a"
                          u"\ufe0f"  # dingbats
                          u"\u3030"
                          "]+", re.UNICODE)
        return re.sub(emoj, '', data)
