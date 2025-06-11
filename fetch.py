import requests
import json
import pandas as pd
from datetime import datetime, timedelta
import pytz # For timezone handling
import os 
from dotenv import load_dotenv

load_dotenv()

# --- Configuration ---
API_URL = os.getenv("API_URL")
API_KEY = os.getenv("API_KEY") # Our team's API Key

DEFAULT_QUERY_TEXT = "US president Trump" # <--- Using the query that reliably returned data
DEFAULT_RESULT_SIZE = 20 # <--- Using a safe result size for stability

def fetch_and_process_data(query_text, result_size):
    """
    Fetches data from the live API and processes it into a DataFrame.
    
    Inputs:
    - query_text (str): The text to query the API for.
    - result_size (int): The number of results to retrieve.
    
    Returns:
    - pd.DataFrame: A DataFrame containing the processed results or an error message.
    """

    # Define headers and payload for the API request
    headers = {
        "Content-Type": "application/json",
        "x-api-key": API_KEY
    }
    payload = {
      "query_text": query_text,
      "result_size": result_size,
      "include_highlights": True,
    }

    try:
        # Attempt to make the API call
        response = requests.post(API_URL, headers=headers, data=json.dumps(payload), timeout=30)
        response.raise_for_status()

        # Decode the JSON response
        json_response = response.json()

        # 
        if 'results' in json_response:
            dataframe = pd.json_normalize(json_response['results'])
            return dataframe
        
        # If the 'results' key is not found, return an empty DataFrame with an error message
        return pd.DataFrame({
            "message": [f"Live API call failed: 'results' key not found in response. Response: {json_response}"]
        })

    
    except requests.exceptions.Timeout:
        # Handle timeout, return appropriate error message
        return pd.DataFrame({
            'message': ["API request timed out. No articles retrieved."]
        })
    
    except requests.exceptions.RequestException as e:
        # Handle other request exceptions, return appropriate error message
        return pd.DataFrame({
            'message': [f"Error retrieving data: {e}. No articles retrieved."]
        })

    except json.JSONDecodeError:
        # Handle JSON decode error, return appropriate error message
        return pd.DataFrame({
            'message': ["Could not decode JSON from API response. Response was not valid JSON."]
        })
    
def fetch_or_retrieve_cached_data(query_text, result_size):
    """
    Fetches data from the live API or retrieves cached data if available.
    
    Inputs:
    - query_text (str): The text to query the API for.
    - result_size (int): The number of results to retrieve.
    
    Returns:
    - pd.DataFrame: A DataFrame containing the processed results or an error message.
    """
    
    try:
        # Check if the cached data file exists
        df_csv = pd.read_csv("cached_data.csv")

        # Check if the query_text exists in the cached data
        if not df_csv[df_csv['query_text'] == query_text].empty:

            # Count the number of cached entries for the query_text
            cached_data_count = df_csv[df_csv['query_text'] == query_text].shape[0]

            # If there are enough cached entries, return the most recent ones
            if cached_data_count >= result_size:
                sorted_cached_df = df_csv[df_csv['query_text'] == query_text].sort_values(by='timestamp', ascending=False)
                return sorted_cached_df.head(result_size)
            
    except FileNotFoundError:

        # If the cached data file does not exist, we will fetch new data
        ...

    # Fetch new data from the live API
    df = fetch_and_process_data(query_text, result_size)

    if 'message' in df.columns and not df['message'].empty:
        # If there is an error message, return it
        return df

    # If the DataFrame is empty, return an empty DataFrame with a message
    if df.empty:
        return pd.DataFrame({
            'message': [f"No articles retrieved for query: '{query_text}'. Please try a different query or check the API status."]
        })
    

    # If we have valid data, we will cache it
    df['query_text'] = query_text
    df.to_csv("cached_data.csv", mode='a', header=not os.path.exists("cached_data.csv"), index=False)

    # Return the DataFrame with the new data
    return df

def clean_articles(dataframe):
    """
    Cleans the articles DataFrame by removing duplicates and ensuring timestamps are in datetime format.
    
    Inputs:
    - dataframe (pd.DataFrame): The DataFrame containing articles.
    
    Returns:
    - None: The DataFrame is modified in place.
    """

    # Coerce timestamps to datetime format, converting errors to NaT
    dataframe["timestamp"] = pd.to_datetime(dataframe["timestamp"], errors='coerce')
    
    # Drop rows with NaT in the timestamp column
    dataframe.dropna(subset=["timestamp"], inplace=True)


def filter_articles_by_time(dataframe:pd.DataFrame, start_date):
    """
    Filters the articles in a DataFrame by a specified time period.

    Inputs:
    - dataframe (pd.DataFrame): The DataFrame containing articles with a 'timestamp' column.
    - start_date (datetime): The start date for filtering.
    
    Returns:
    - pd.DataFrame: A DataFrame containing articles within the specified time period."""

    # Get the current date and time in London timezone
    london_tz = pytz.timezone('Europe/London')
    current_date = datetime.now(london_tz)

    # Ensure DataFrame timestamps are timezone-aware and converted to London timezone
    if dataframe['timestamp'].dt.tz is None:
        dataframe['timestamp'] = dataframe['timestamp'].dt.tz_localize('UTC').dt.tz_convert(london_tz)
    else:
        dataframe['timestamp'] = dataframe['timestamp'].dt.tz_convert(london_tz)

    if start_date.tzinfo is None:
        start_date = london_tz.localize(start_date)

    # Filter the DataFrame for articles within the specified time period
    filtered_df = dataframe[dataframe['timestamp'] >= start_date].copy()
    return filtered_df.sort_values(by='timestamp', ascending=True)

# --- Main execution block for console output ---
if __name__ == "__main__":

    # Fetch data from the live API or retrieve cached data
    df = fetch_or_retrieve_cached_data(DEFAULT_QUERY_TEXT, DEFAULT_RESULT_SIZE)

    # Coerce timestamps to datetime format and clean the DataFrame
    clean_articles(df)

    # Filter the DataFrame by time for articles from yesterday
    yesterday_df = filter_articles_by_time(df, datetime.now(pytz.timezone('Europe/London')) - timedelta(days=1))
    
    # Display the results
    print(yesterday_df[["id", "timestamp", "summary"]])