# Import some libraries

import requests
import json
import pandas as pd

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

def get_data(query: str, results: int):
    """Gets data from the Amplyfi API on a query. 

    Args:
        query (str): The query to send
        results (int): Amount of results needed. 

    Returns:
        Dataframe: A pandas dataframe containing all data retrieved from the request
    """
    
    cache_df = pd.read_csv("cache.csv")
    if len(cache_df[cache_df["query"] == query]) > 0:
        return cache_df[cache_df["query"] == query]

    # Edit the below to get different data
    payload = {
    "query_text": query,
    "result_size": 10,
    "include_highlights":True,
    "ai_answer": "basic"
    }

    response = requests.post(API_URL, headers=headers, data=json.dumps(payload))
    json_response = response.json()
    
    if json_response['message'] == 'Endpoint request timed out':
        raise Exception('Endpoint request timed out, try again')
    
    df = pd.json_normalize(json_response)
    df["query"] = query
    
    csv_path = "cache.csv"
    df.to_csv(csv_path, mode='a', header=not os.path.exists(csv_path), index=False)

    
    return df