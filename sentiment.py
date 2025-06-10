import pandas as pd
import spacy
import nltk
from nltk.sentiment.vader import SentimentIntensityAnalyzer as SIA

# Load the spaCy model for sentiment analysis and entity recognition
spacy.cli.download("en_core_web_sm")
nlp = spacy.load("en_core_web_sm")

# Download the VADER lexicon for sentiment analysis
nltk.download("vader_lexicon")

# Initialize the VADER sentiment intensity analyzer
sia = SIA()

def sentiment_category(score):
    """
    Categorizes the VADER compound score into sentiment groups.
    """
    if score <= -0.6:
        return "very negative"
    elif score < -0.2:
        return "negative"
    elif score <= 0.2:
        return "neutral"
    elif score < 0.6:
        return "positive"
    else:
        return "very positive"

def analyze_sentiment(dataframe: pd.DataFrame):
    """
    Analyses the sentiment of the 'title' column in the given DataFrame using VADER.
    
    Inputs:
    - dataframe (pd.DataFrame): A DataFrame containing a 'title' column with text data.

    Returns:
    - None: The function modifies the DataFrame in place by adding a 'sentiment' column.
    """

    dataframe['sentiment'] = dataframe['title'].apply(lambda x: sia.polarity_scores(x)['compound'])
    dataframe['sentiment_category'] = dataframe['sentiment'].apply(sentiment_category)


def extract_entities(text):
    """
    Extracts unique people and organizations from the given text using spaCy.
    
    Inputs:
    - text (str): The input text from which to extract entities.
    
    Returns:
    - dict: A dictionary with two keys:
        - 'people': A list of unique people names found in the text.
        - 'organizations': A list of unique organization names found in the text.
    """

    # If non-string or empty, return empty lists
    if not isinstance(text, str) or not text.strip():
        return {'people': [], 'organizations': []}

    # Process the text with spaCy
    doc = nlp(text)

    # Extract unique people
    people = list(set([ent.text for ent in doc.ents if ent.label_ == 'PERSON']))

    # Extract unique organizations
    organizations = list(set([ent.text for ent in doc.ents if ent.label_ == 'ORG']))

    # Return resulting lists
    return {'people': people, 'organizations': organizations}

def package_articles_with_sentiment_info(dataframe: pd.DataFrame):
    """
    Packages articles with sentiment analysis and entity extraction.
    
    Inputs:
    - dataframe (pd.DataFrame): A DataFrame containing a 'title' and 'summary' column with text data.
    
    Returns:
    - None: The function modifies the DataFrame in place by adding 'sentiment', 'people', and 'organizations' columns.
    """

    analyze_sentiment(dataframe)

    dataframe['people'] = pd.Series(dtype=object)
    dataframe['organizations'] = pd.Series(dtype=object)

    for index, row in dataframe.iterrows():
        entities = extract_entities(row['summary'])


        dataframe.at[index, 'people'] = entities['people']
        dataframe.at[index, 'organizations'] = entities['organizations']

def update_vader_lexicon():
    nltk.download("vader_lexicon")

