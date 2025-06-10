# Import some libraries

import requests
import json
import nltk
import re
import pandas as pd

# from nltk.sentiment.vader import SentimentIntensityAnalyzer
# nltk.download('vader_lexicon')

# importing os module for environment variables
import os
# importing necessary functions from dotenv library
from dotenv import load_dotenv, dotenv_values 
# loading variables from .env file
load_dotenv() 

# API endpoint from the newly deployed service

API_URL = "https://zfgp45ih7i.execute-api.eu-west-1.amazonaws.com/sandbox/api/search"
API_KEY = os.getenv("API_KEY")

query_text = input("What is the query text? ")

headers = {
    "Content-Type": "application/json",
    "x-api-key": API_KEY
}

# Edit the below to get different data
payload = {
  "query_text": query_text,
  "result_size": 1,
  "include_highlights":True,
  "ai_answer": "basic"
}

response = requests.post(API_URL, headers=headers, data=json.dumps(payload))
json_response = response.json()

results = json_response.get("results")

print(json_response)