# -*- coding: utf-8 -*-
"""Scraping the trending IDs, typically 300, filter them based on english language and latest number of articles pulished within"""

import requests
import time
import json
import pandas as pd
import traceback
from datetime import date
import os
from dotenv import load_dotenv
load_dotenv()
#nltk.download('punkt')

class TrendingNews:
    '''
    Class to scrap the trending news IDs, article title, article text from Google Trends.
    '''

    def __init__(self):
        '''
        Fetches the trending news data by calling other functions, processes it, and saves it to files.

        Class global variables:
        all_trending_ids - stores the trending article ids in a lookup table, so that no article is processed repeatedly
        trending_ids - Stores the information regarding the articles scraped in a day
        '''
        # Create a soup of the Google trending news app
        json_content = self.get_soup(os.getenv("google_news_url"))
        all_story_ids = json_content['trendingStoryIds']

        self.initialize_all_trending_ids()

        # Store the trending ids and other information of a story into a dataset
        self.trending_ids = self.get_story_ids(all_story_ids)
        
        # Save the trending news IDs to the lookup table
        self.all_trending_ids.to_csv(f'{os.getenv("temp_folder")}/all_trending_ids.csv', index=False)

    def get_soup(self, url):
        '''
        Fetches and returns the content of a webpage as JSON.

        Args:
        url: URL of the webpage

        Returns:
        content_json: JSON content of the webpage
        '''
        try:
            user_agent = "'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1916.47 Safari/537.36'"
            html = requests.get(url, headers={'User-Agent': user_agent}).text
            time.sleep(5)
            content_json = json.loads(html[5:])
            return content_json
        except Exception as e:
            print("Error fetching content:", e)
            return ""

    def initialize_all_trending_ids(self):
        '''
        Initializes the lookup table for storing trending IDs
        '''
        try:
            self.all_trending_ids = pd.read_csv(f'{os.getenv("temp_folder")}/all_trending_ids.csv')
        except FileNotFoundError:
            self.all_trending_ids = pd.DataFrame(columns=['id', 'story'])

    def get_story_ids(self, all_story_ids):
        '''
        Extracts story IDs from a list of all story IDs. Stores the information of a story by calling get_latest_article function

        Args:
        all_story_ids: List of all trending story IDs scrapped from google news

        Returns:
        current_trending_articles: List of dictionaries containing ID, stories of all the trending articles pf that day
        '''
        current_trending_articles = []
        for id in all_story_ids:
            article_dict = dict()

            # fetch the information for an ID if it is not processed already
            if self.all_trending_ids['id'].eq(id).any():
                continue
            
            #Capture the English stories only
            if id[-2:] != 'en':
                continue
            
            article_dict['id'] = id

            #calling the get_latest_article function to fetch information regarding a story ID
            num_latest_articles, article_dict['stories'], article_dict['all_articles_keywords'] = self.get_latest_articles(id)
            
            if article_dict['all_articles_keywords'] is not None:
                article_dict['all_articles_keywords'] = article_dict['all_articles_keywords'].split(", ")
            
            # if number of articles regarding an ID is less than 2 means it is a less trending story, then skip that story and related articles
            if num_latest_articles is not None:
                if num_latest_articles < 2:
                    continue
                
                current_trending_articles.append(article_dict)
                self.all_trending_ids.loc[len(self.all_trending_ids)] = [id, article_dict['stories']]
                
        return current_trending_articles

    def get_latest_articles(self, id):
        '''
        Extracts latest articles for a given story ID.

        Args:
        - id: ID of the story

        Returns:
        - latest_num_articles: Number of latest articles regarding that story
        - temp_dict: Dictionary containing information about latest articles
        - story_keywords: Keywords related to the story
        '''
        temp_dict = dict()
        story_url = "https://trends.google.com/trends/api/stories/"+id+"?hl=en-US&tz=-330"
        barflag, artflag = 0, 0
        all_stories_content = []
        story_content_json = self.get_soup(story_url)
        
        if story_content_json != '':
            latest_num_articles = -1
            story_keywords = story_content_json['title']
            
            # Arranging some conditions based on JSON data 
            for i in range(len(story_content_json['widgets'])):
                if (barflag == 0) and ('barData' in story_content_json['widgets'][i]):
                    barflag = 1
                if (artflag == 0) and ('articles' in story_content_json['widgets'][i]):
                    artflag = 1
                    all_stories_content = story_content_json['widgets'][i]['articles']
                if (barflag == 1) and (artflag == 1):
                    latest_num_articles = story_content_json['widgets'][i]['barData'][-1]['articles'] + story_content_json['widgets'][i]['barData'][-2]['articles']
                    break
            
            if len(all_stories_content) == 0:
                return None, None, None
            
            today_date = date.today()
            temp_dict['title'] = all_stories_content[0]['title']
            temp_dict['url'] = all_stories_content[0]['url']
            temp_dict['source'] = all_stories_content[0]['source']
            temp_dict['image_url'] = all_stories_content[0]['imageUrl']
            temp_dict['date'] = str(today_date)
            return latest_num_articles, temp_dict, story_keywords
        else:
            return None, None, None