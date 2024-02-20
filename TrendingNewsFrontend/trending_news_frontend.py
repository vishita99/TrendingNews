import requests
import random
import streamlit as st
from annotated_text import annotated_text
from annotated_text import annotation
import feedparser
import os
from dotenv import load_dotenv
load_dotenv()

def get_random_colour_for_text_highlight(last_colors):
    colors = ["#FFFFFF", "#FFFF00", "#FF0000", "#008000", "#0000FF", "#800080", "#FFA500", "#FFC0CB", "#008080", "#E6E6FA", "#FFD700", "#C0C0C0", "#40E0D0", "#FF00FF", "#00FF00", "#800000", "#00FFFF", "#DDA0DD", "#FFBF00"]
    if len(last_colors)>0:
        for last_color in last_colors:
            if (last_color in colors) & (len(colors)>3):
                colors.remove(last_color)
    return random.choice(colors)

def get_annotated_topics(keywords, topic_description, max_number_topics):
    annotation_text = ''
    for count, keyword in enumerate(keywords):
        if count >= max_number_topics:
            break
        annotation_text += ''', annotation("{}", "{}", color='{}')'''.format(keyword, topic_description[keyword]['topic_number'], topic_description[keyword]['color'])
    return annotation_text

def get_description_of_topic(used_colors, topic_number):
    description = dict()
    color = get_random_colour_for_text_highlight(used_colors)
    description['color'] = color
    description['topic_number'] = topic_number
    used_colors.append(color)
    return description, used_colors

def get_topic_number_and_color(data):
    topic_description, used_colors = dict(), list()
    ners, topics = data["NER"], data["all_articles_keywords"]
    # show 4 topics as headers and others inside
    total_topics = max(4,len(topics))
    for count, topic in enumerate(topics):
        description, used_colors = get_description_of_topic(used_colors, count+1)
        topic_description[topic] = description
    for ner in ners:
        if ner in topics:
            continue
        description, used_colors = get_description_of_topic(used_colors, total_topics)
        total_topics+=1
        topic_description[ner] = description
    return topic_description

def get_summary_with_annotated_ners(data, topic_description):
    ners = data['NER']
    summary_text = data["article_summary"]
    for entity in ners:
        summary_text =  summary_text.replace(entity, '''""", annotation('{}', '{}', color='{}'), """'''.format(entity, topic_description[entity]['topic_number'], topic_description[entity]['color']))
    summary_text = '"""{}"""'.format(summary_text)
    return summary_text


def news_card(data):
    if data is not None:
        with st.container():
            st.subheader(data["stories"]["title"].replace('\n',' '))
            st.text(data["stories"]["source"])
            st.text(data["stories"]["date"])
            topic_description = get_topic_number_and_color(data)
            st.image(data["stories"]["image_url"], width=600, use_column_width=True)
            eval('''annotated_text("Topics: " {})'''.format(get_annotated_topics(data["all_articles_keywords"], topic_description, max_number_topics=4)))
            st.markdown(" ")
            summary_text = get_summary_with_annotated_ners(data, topic_description)
            eval('annotated_text({})'.format(summary_text))
            # st.markdown(summ)
            st.markdown("[Read More](" + data["stories"]["url"] + ")")

def get_data():
    response = requests.get(url=os.getenv("fetch_data_api")).json()
    if response['success']:
        return response['data']
    return None


if __name__ == "__main__":
    st.title("Trending News")
    st.spinner("Loading News")
    data = get_data()
    if data is None:
        st.subheader("Error loading news")
    else:
        for _ in data:
            news_card(_)
    