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

    print(df['people'])
    print(df['organizations'])

    all_people = df['people'].explode().dropna().unique().tolist()
    all_orgs = df['organizations'].explode().dropna().unique().tolist()

    selected_people = st.sidebar.multiselect("Select people to focus on:", all_people)
    selected_orgs = st.sidebar.multiselect("Select organizations to focus on:", all_orgs)

    filtered_df = df.copy()

    if selected_people:
        filtered_df = filtered_df[filtered_df['people'].apply(lambda people_list: any(p in people_list for p in selected_people))]
    if selected_orgs:
        filtered_df = filtered_df[filtered_df['organizations'].apply(lambda org_list: any(o in org_list for o in selected_orgs))]


    st.header("Event Timeline")
    
    fig = px.timeline(
            filtered_df,
            x_start="timestamp",
            x_end=filtered_df['timestamp'] + pd.Timedelta(minutes=120),
            y="sentiment_category",
            color='sentiment',          # This line will now work correctly
            color_continuous_scale='RdBu_r', # Use a Red-to-Blue color scale
            range_color=[-1, 1],        # Lock the color scale from -1 to 1
            hover_name='summary'        # Show full summary on hover
        )
    
    fig.update_yaxes(visible=False, showticklabels=False)
    st.plotly_chart(fig, use_container_width=True)

    # 2. Create the Data Table
    st.header("Filtered Articles & Data")
    # Define columns to show, including the new sentiment score
    display_columns = ['timestamp', 'summary', 'sentiment', 'people', 'organizations', 'url']
    st.dataframe(filtered_df[display_columns])

if __name__ == "__main__":
    init_app()