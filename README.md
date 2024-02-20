
# Trending News

## Overview

Trending News is a web application that provides users with summarized recent trending news from around the world. The web app is developed using Streamlit, and APIs are developed using Flask. The process involves scraping data from Google Trending News articles, generating summaries using the Pegasus model, extracting keywords with the DeBERTa model, and applying NLTK to fetch Named Entity Recognition (NER) details.

## Features

- Integration of Google Trending News data.
- Use of Pegasus model for article summarization.
- DeBERTa model for keyword extraction.
- Named Entity Recognition (NER) using NLTK.
- Two APIs: `fetch_data` for getting the stored news and `update_data` for updating recent trending news.

## Installation

1. Clone the repository:

   ```bash
   git clone https://github.com/vishita99/Trending-News.git\

## Install Dependencies

1. Navigate to TrendingNews folder 

    ```bash
   cd TrendingNews

2. install dependencies
   ```bash
   pip install -r requirements.txt

## Usage

### Running the backend flask server
    python app.py

#### For updating data everytime:
The python server will start running, once successful run `<your_server_address>/update_data`. It will take a few hours to update the data...

#### Once the python server is up and running, open a different terminal:

### Navigating the streamlit folder

    cd TrendingNewsStreamlit

### Running the streamlit

    streamlit run trending_news_frontend.py

Visit the URL provided by Streamlit in your browser.