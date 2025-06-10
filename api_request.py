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
    
    try:
        cache_df = pd.read_csv("cache.csv")
        if len(cache_df[cache_df["query"] == query]) > 0:
            print("cached result found ")
            return cache_df[cache_df["query"] == query]
    except:
        print("no file exists at 'cache.csv', continuing to make request")

    # Edit the below to get different data
    payload = {
    "query_text": query,
    "result_size": results,
    "include_highlights":True
    }

    print("making request")
    response = requests.post(API_URL, headers=headers, data=json.dumps(payload), timeout=30)
    json_response = response.json()
    
    if json_response['message'] == 'Endpoint request timed out':
        raise Exception('Endpoint request timed out, try again')
    
    df = pd.json_normalize(json_response)
    df["query"] = query
    
    csv_path = "cache.csv"
    df.to_csv(csv_path, mode='a', header=not os.path.exists(csv_path), index=False)

    
    return df

def fetch_and_process_data(query_text, result_size):

    csv_path = "cache.csv"

    try:
        cache_df = pd.read_csv(csv_path)
        if len(cache_df[cache_df["query"] == query_text]) > 0:
            print("cached result found ")
            return cache_df[cache_df["query"] == query_text]
    except:
        print("no file exists at 'cache.csv', continuing to make request")

    headers = {
        "Content-Type": "application/json",
        "x-api-key": API_KEY
    }
    payload = {
      "query_text": query_text,
      "result_size": result_size,
      "include_highlights": True
    }

    try:
        response = requests.post(API_URL, headers=headers, data=json.dumps(payload), timeout=30) # Add timeout
        response.raise_for_status() # Raise HTTPError for bad responses (4xx or 5xx)
        json_response = response.json()

        if 'results' in json_response:
            df = pd.json_normalize(json_response['results'])
            df['timestamp'] = pd.to_datetime(df['timestamp'], errors='coerce')
            df.dropna(subset=['timestamp'], inplace=True)
            df = df.sort_values(by='timestamp', ascending=True).reset_index(drop=True)
            df['query'] = query_text

            
            df.to_csv(csv_path, mode='a', header=not os.path.exists(csv_path), index=False)

            
            return df
        else:
            raise Exception(f"API Response did not contain 'results'. Response: {json_response}")
    except requests.exceptions.Timeout:
        raise Exception("API request timed out. Displaying cached data if available, or try a smaller result size.")
    except requests.exceptions.RequestException as e:
        raise Exception(f"Error making API request: {e}. Displaying cached data if available.")
    except json.JSONDecodeError:
        raise Exception("Could not decode JSON from API response.")
