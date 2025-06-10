import streamlit as st
import plotly.express as px
import pandas as pd
from fetch import fetch_or_retrieve_cached_data, clean_articles
import sentiment
from sentiment import package_articles_with_sentiment_info

@st.cache_data
def get_display_data():
    df = fetch_or_retrieve_cached_data("AI Regulation", 50)
    clean_articles(df)
    package_articles_with_sentiment_info(df)

    return df

    ...

def init_app():
    st.set_page_config(layout="wide")

    df = get_display_data()

    st.title("Event Unfolder: A Real-Time Story Tracker ⏳")

    st.sidebar.header("Filter by Entities")

    selected_people = st.sidebar.multiselect("Select people to focus on:", ["bob", "frank", "dave", "belinda"])
    selected_orgs = st.sidebar.multiselect("Select organizations to focus on:", ["acme", "globex", "initech", "stark"])

    st.header("Event Timeline")
    
    fig = px.timeline(
            df,
            x_start="timestamp",
            x_end=df['timestamp'] + pd.Timedelta(minutes=120),
            y="sentiment_category",
            color='sentiment',          # This line will now work correctly
            color_continuous_scale='RdBu_r', # Use a Red-to-Blue color scale
            range_color=[-1, 1],        # Lock the color scale from -1 to 1
            hover_name='summary'        # Show full summary on hover
        )
    
    fig.update_yaxes(visible=False, showticklabels=False)
    st.plotly_chart(fig, use_container_width=True)

    st.header("Filtered Articles & Data")

if __name__ == "__main__":
    init_app()