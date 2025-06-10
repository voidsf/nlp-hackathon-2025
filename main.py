# Import some libraries

import requests
import json
import nltk
import re
import pandas as pd

from nltk.sentiment.vader import SentimentIntensityAnalyzer
nltk.download('vader_lexicon')

# importing os module for environment variables
import os
# importing necessary functions from dotenv library
from dotenv import load_dotenv, dotenv_values 
# loading variables from .env file
load_dotenv() 

# API endpoint from the newly deployed service

API_URL = "https://zfgp45ih7i.execute-api.eu-west-1.amazonaws.com/sandbox/api/search"
API_KEY = os.getenv("API_KEY")

headers = {
    "Content-Type": "application/json",
    "x-api-key": API_KEY
}

# Edit the below to get different data
payload = {
  "query_text": "trump musk social media",
  "result_size": 10,
  "include_highlights":True,
  "ai_answer": "basic"
}

response = requests.post(API_URL, headers=headers, data=json.dumps(payload))
json_response = response.json()

print(json_response)