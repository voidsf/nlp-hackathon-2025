import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
import string
nltk.download('punkt')
nltk.download('punkt_tab')
nltk.download('stopwords')

def extract_keywords(sentence):
    """
    Extract meaningful keywords from a sentence by removing stopwords and non-alphabetic tokens.

    Parameters
    ----------
    sentence : str
    The input text from which to extract keywords. Must be a string; passing other types will raise an exception.

    Returns
    -------
    list of str
    A list of lowercase alphabetic tokens from the sentence, excluding English stopwords as provided by NLTK.

    Notes
    -----
    - Relies on NLTK’s `word_tokenize` and `stopwords.words('english')`. Ensure 'punkt' and 'stopwords' corpora are available.
    - Tokens are converted to lowercase before filtering.
    - Only tokens where `str.isalpha()` is True are kept.
    """
all_keywords = []
for title in df['title']:
    if isinstance(title, str):
        kws = extract_keywords(title)
    else:
        kws = []  
    all_keywords.append(kws)

df['keywords'] = all_keywords

# print(df[['title', 'keywords']].head())