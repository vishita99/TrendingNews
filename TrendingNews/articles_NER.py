"""
This fetches the NER from article summary
"""

import nltk
import traceback

class ArticleNER:
    def __init__(self, trending_articles):
        """
        Initializes the ArticleKeywords object with the provided dataframe of current trending articles and checks if NER is already present as keyword
        
        Args:
            trending_articles (pandas df): dataframe of list of trending articles with summaries.
        """
        self.trending_articles_with_NER = trending_articles

        self.caller_function()

    def caller_function(self):
      '''
      Iterates over all stories and calls the fetch NER and check for duplicate keywords functions
      '''
      for i in range(len(self.trending_articles_with_NER)):
          art_ner = self.tagging(self.trending_articles_with_NER[i]['article_summary'])
          if len(art_ner) > 0:
              self.trending_articles_with_NER[i]['NER'] = art_ner
              self.trending_articles_with_NER[i]['NER'] = self.check_repeat_NER(
                  self.trending_articles_with_NER[i]['NER'], self.trending_articles_with_NER[i]['all_articles_keywords'])
          else:
              self.trending_articles_with_NER[i]['NER'] = []

    def check_repeat_NER(self, ner, keywords):
        """
        Checks for repeated words in named entities and already present keywords and returns unique named entities.
        
        Args:
            ner (list): List of named entities.
            keywords (list): List of keywords.
        
        Returns:
            list: List of unique named entities.
        """
        words_to_remove_ner = [word1 for word1 in ner if any(word1 in word2 and word1 != word2 for word2 in ner)]
        unique_ner = [word for word in ner if word not in words_to_remove_ner]
        words_to_remove_keywords = [word1 for word1 in unique_ner if any(word1 in word2 or word1 == word2 for word2 in keywords)]
        unique_ner_keywords = [word for word in unique_ner if word not in words_to_remove_keywords]
        return unique_ner_keywords

    def tagging(self, text):
        """
        Performs named entity recognition on the given text and returns a list of named entities.
        
        Args:
            text (str): Input text.
        
        Returns:
            named_entitied (list): List of named entities.
        """
        text = text.replace("<n>", " ")
        tokens = nltk.word_tokenize(text)
        tagged_tokens = nltk.pos_tag(tokens)
        ner_chunks = nltk.ne_chunk(tagged_tokens)
        named_entities = []
        for chunk in ner_chunks:
            if hasattr(chunk, 'label') and (chunk.label() in ['PERSON', 'GPE', 'ORGANIZATION', 'FACILITY', 'PRODUCT', 'EVENT']):
                named_entities.append(' '.join(c[0] for c in chunk.leaves()))
        return list(set(named_entities))

