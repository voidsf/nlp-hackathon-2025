import pandas as pd
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
import string

# Ensure NLTK resources are available
nltk.download('punkt')
nltk.download('stopwords')

def extract_keywords(sentence):
    """
    Extract meaningful keywords from a sentence by removing stopwords and non-alphabetic tokens.
    """
    if not isinstance(sentence, str):
        return []
    tokens = word_tokenize(sentence.lower())
    stop_words = set(stopwords.words('english'))
    keywords = [word for word in tokens if word.isalpha() and word not in stop_words]
    return keywords

def get_common_keywords_df(df):
    """
    Given a DataFrame with columns 'id' and 'title', extract keywords from titles,
    and return a DataFrame of keywords that appear in more than one title, along with the list of IDs and the count.

    Parameters
    ----------
    df : pandas.DataFrame
        DataFrame containing at least 'id' and 'title' columns.

    Returns
    -------
    common_keywords_df : pandas.DataFrame
        DataFrame with columns ['keyword', 'ids', 'count'] for keywords that appear in more than one title.
    """
    # Extract keywords for each title
    df_copy = df.copy()
    df_copy['keywords'] = df_copy['title'].apply(lambda t: extract_keywords(t) if isinstance(t, str) else [])
    
    # Explode keywords
    df_exploded = df_copy.explode('keywords')
    
    # Aggregate: list of IDs and count of unique IDs per keyword
    agg = (
        df_exploded
        .groupby('keywords')['id']
        .agg(ids=lambda x: list(x.unique()), count=lambda x: x.nunique())
        .reset_index()
        .rename(columns={'keywords': 'keyword'})
    )
    
    # Filter to common keywords (count > 1)
    common_keywords_df = agg[agg['count'] > 1].reset_index(drop=True)
    return common_keywords_df