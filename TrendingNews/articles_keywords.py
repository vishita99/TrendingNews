"""
This script fetches the keywords from article text
"""

import time
import traceback
import requests
import os
from dotenv import load_dotenv
load_dotenv()

#get the API of Deberta huggingface model
API_URL = os.getenv("API_Deberta")
headers = {"Authorization": "Bearer {}".format(os.getenv("deberta_authorisation_key"))}

class ArticleKeywords:
    def __init__(self, trending_articles):
        """
        Initializes the ArticleKeywords object with the provided dataframe of current trending articles
        
        Args:
            trending_articles (pandas df): dataframe of list of trending articles.
        """
        self.trending_articles_with_keywords = self.get_keywords(trending_articles)
            
    def query(self, payload):
        """
        Calls the Deberta API with the provided payload and returns the JSON response.
        
        Args:
            payload (dict): Payload for the POST request.
        
        Returns:
            dict: JSON response from the API.
        """
        response = requests.post(API_URL, headers=headers, json=payload)
        return response.json()
      
    def call_query(self, payloads):
        """
        Recursively calls the Deberta model API by calling the "query" function until a successful response is received, handling errors and delays.
        
        Args:
            payloads (dict): Payloads for the POST request.
        
        Returns:
            dict: JSON response from the API.
        """
        score = self.query(payloads)
        if 'error' in score and 'estimated_time' in score:
            time.sleep(int(score['estimated_time']) + 5)
            return self.call_query(payloads)
        return score
      
    def get_keywords(self, current_articles):
        """
        Iterates through all articles and extracts keywords for each.
        
        Args:
            current_articles (pandas df): Dataframe of list of current articles.
        
        Returns:
            current_articles (df): dataframe of current articles with extracted keywords.
        """
        for i in range(len(current_articles)):
            current_articles[i]['final_keywords'] = ''
            try:
                score = self.call_query({
                    "inputs": current_articles[i]['article_text'],
                    "parameters": {"candidate_labels": current_articles[i]['all_articles_keywords'], "multi_label": True},
                })
                
                if score['scores'][0] > 0.2:
                    current_articles[i]['final_keywords'] = score['labels'][0:3]
            except Exception as e:
                traceback.print_exc()
                pass
        return current_articles
