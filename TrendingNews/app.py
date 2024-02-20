"""
This script defines a Flask application to fetch and update trending news data.
"""

from flask import Flask, jsonify
import pandas as pd
from trending_news import TrendingNews
from articles_text import ArticleText
from articles_summary import ArticleSummary
from articles_keywords import ArticleKeywords
from articles_NER import ArticleNER
import json
import warnings
import os
from dotenv import load_dotenv
load_dotenv()

app = Flask(__name__)

@app.route('/fetch_data', methods=['GET'])
def fetch_data():
    """
    Fetches the current trending news data that is stored in the CSV file and returns it as JSON.
    
    Returns:
        JSON response: Success status along with the fetched data if successful, otherwise a failure status.
    """
    try:
        data = pd.read_csv(f'{os.getenv("temp_folder")}/current_trending_news.csv')
        # Convert data to JSON format
        json_data = [json.loads(row) for row in data['all_info']]
        resp = jsonify(success=True, data=json_data)
        return resp
    except Exception as e:
        resp = jsonify(success=False)
        return resp

@app.route('/update_data')
def update_data():
    """
    Updates the current trending news data by fetching new news, extracting text, summarizing,
    extracting keywords, and performing named entity recognition (NER). The updated data is stored
    in a CSV file.
    
    Returns:
        JSON response: Success status if the update is successful, otherwise a failure status.
    """
    try:
        # Get trending news IDs
        news = TrendingNews()
        current_trending_ids = news.trending_ids
        
        # Extract text from articles
        text = ArticleText(current_trending_ids)
        
        # Summarize articles
        summary = ArticleSummary(text.trending_articles_with_text)
        
        # Extract keywords from articles
        keywords = ArticleKeywords(summary.trending_articles_with_summary)
        
        # Perform NER on articles
        NER = ArticleNER(keywords.trending_articles_with_keywords)
        current_trending_ids = NER.trending_articles_with_NER
        
        # Store and save updated data into a CSV file
        current_trending_news = pd.DataFrame(columns=['all_info'])
        current_trending_news['all_info'] = current_trending_ids
        current_trending_news['all_info'] = current_trending_news['all_info'].apply(json.dumps)
        current_trending_news.to_csv(f'{os.getenv("temp_folder")}/current_trending_news.csv', index=False)
        
        resp = jsonify(success=True)
        return resp
    except Exception as e:
        resp = jsonify(success=False)
        return resp

if __name__ == '__main__':
    app.run(debug=True)
