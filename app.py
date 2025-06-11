import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from fetch import fetch_or_retrieve_cached_data, clean_articles, filter_articles_by_time
import sentiment
from sentiment import package_articles_with_sentiment_info
import requests
import os 
from dotenv import load_dotenv
import ast
from datetime import timedelta, datetime

load_dotenv()

@st.cache_data
def get_display_data(query, filter):
    df = fetch_or_retrieve_cached_data(query, 50)
    clean_articles(df)
    package_articles_with_sentiment_info(df)

    if filter:
        return filter_articles_by_time(df, filter)
    
    return df

    ...

def get_ai_summary(query, articles_text):

    prompt = f"""
    Please give me a concise overall summary of the following news article summaries, staying broadly on topic.
    Preface with 'Here's a summary of the latest news articles on '{query}', or similar.
    Aim for two or three paragraphs.
    News Summaries:
    {articles_text}
    """

    chatHistory = [{"role": "user", "parts": [{"text": prompt}]}]
    payload = {"contents": chatHistory}
    # IMPORTANT: Replace with your own key from aistudio.google.com/app/apikey
    apiKey = os.getenv("GEMINI_API_KEY")
    apiUrl = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={apiKey}"

    try:
        response = requests.post(apiUrl, headers={'Content-Type': 'application/json'}, json=payload)
        response.raise_for_status()
        result = response.json()

        if (result.get('candidates') and result['candidates'][0].get('content') and result['candidates'][0]['content'].get('parts')):
            return result['candidates'][0]['content']['parts'][0]['text']
        else:
            return "The AI model could not generate a summary based on the provided text."
    except requests.exceptions.RequestException as e:
        return f"An error occurred while contacting the AI model: {e}"



def init_app():
    st.set_page_config(layout="wide")


    st.title("Newsyfi")
    st.subheader("Your AI-Powered News Briefing")

    search_bar = st.sidebar.text_input("Search:", "")


    time_range_options = {"Last 24 Hours": timedelta(days=1), "Last 7 Days": timedelta(days=7), "Last 30 Days": timedelta(days=30), "All Time": None}
    selected_range_label = st.sidebar.radio("Time Range:", options=list(time_range_options.keys()))

    delta = time_range_options[selected_range_label]

    if search_bar:
        df = get_display_data(search_bar, datetime.now() - delta if delta else None)
    else:
        df = get_display_data("Cake recipes", datetime.now() - delta if delta else None)



    print(selected_range_label)


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

    

    # --- MAIN PANEL ---
    if filtered_df.empty:
        st.warning("No articles match your current filter criteria.")
    else:
        st.success(f"Displaying {len(filtered_df)} articles matching your criteria.")

        # --- SUMMARY SECTION ---
    st.subheader("Summary")
    if st.button("✨ Generate Briefing"):
        with st.spinner("The AI analyst is reviewing the articles..."):
            text_to_summarize = "\n".join(filtered_df['summary'].head(20).tolist())
            st.info(get_ai_summary(search_bar if search_bar else "Cake recipes", text_to_summarize))

            #st.session_state.summary = get_ai_summary(text_to_summarize)

    # if 'summary' in st.session_state:
    #     st.info(st.session_state.summary)
    st.divider()


    st.header("Event Timeline")

    # --- TWO-COLUMN LAYOUT ---
    col1, col2 = st.columns(2, gap="medium") # Using a simpler syntax and adding a gap

    final_filtered_df = filtered_df.copy()

    with col1:
        st.subheader("Sentiment Trend & Momentum")

        tr_options = {
            "Last 24 Hours": timedelta(hours=1), 
            "Last 7 Days": timedelta(hours=12), 
            "Last 30 Days": timedelta(days=2), 
            "All Time": timedelta(days=2)}

        sentiment_over_time = final_filtered_df.set_index('timestamp')['sentiment'].resample(tr_options[selected_range_label]).mean().dropna()
        sentiment_momentum = sentiment_over_time.diff().rolling(window=2).mean()

        fig_momentum = go.Figure()
        fig_momentum.add_trace(go.Bar(x=sentiment_over_time.index, y=sentiment_over_time.values, name='Hourly Avg. Sentiment', marker_color='#add8e6'))


        fig_momentum.add_trace(go.Scatter(x=sentiment_momentum.index, y=sentiment_momentum.values, name='Sentiment Momentum', mode='lines', line=dict(color='#ff4b4b', width=3)))
        

        fig_momentum.update_layout(
            title_text='Is the narrative getting better or worse?',
            yaxis_title='Sentiment Score / Momentum',
            legend=dict(yanchor="top", y=0.99, xanchor="left", x=0.01),
            height=400,
            margin=dict(t=20, b=40)
        )
        st.plotly_chart(fig_momentum, use_container_width=True)

    with col2:
        st.subheader("Timeline View")
        final_filtered_df['task'] = final_filtered_df['timestamp'].dt.strftime('%Y-%m-%d %H:%M') + " - " + final_filtered_df['summary'].str[:40] + "..."

        fig_timeline = px.timeline(
            filtered_df,
            x_start="timestamp",
            x_end=filtered_df['timestamp'] + pd.Timedelta(minutes=120),
            y="sentiment_category",
            color='sentiment',          # This line will now work correctly
            color_continuous_scale='RdBu_r', # Use a Red-to-Blue color scale
            range_color=[-1, 1],        # Lock the color scale from -1 to 1
            hover_name='summary'        # Show full summary on hover
        )

        fig_timeline.update_yaxes(visible=False, showticklabels=False)
        fig_timeline.update_layout(
            title_text=f"Timeline of {len(final_filtered_df)} Articles",
            height=400,
            margin=dict(t=20, b=40)
        )
        st.plotly_chart(fig_timeline, use_container_width=True)

    st.divider()

    # --- INTERACTIVE DATA TABLE SECTION ---
    st.subheader("Article Explorer")
    st.info("Click on any row in the table below to see a detailed deep dive.")

    # Using st.dataframe with on_select for a cleaner, read-only interactive table
    selection = st.dataframe(
        filtered_df[['timestamp', 'summary', 'sentiment', 'people', 'organizations', 'url']],
        on_select="rerun",
        selection_mode="single-row",
        key="article_selector_df",
        hide_index=True,
        column_config={
            "timestamp": st.column_config.DatetimeColumn("Time (UTC)", format="D MMM, h:mmA"),
            "summary": "Article Summary",
            "sentiment": st.column_config.NumberColumn("Sentiment", format="%.2f"),
            "people": "People",
            "organizations": "Organizations",
            "url": st.column_config.LinkColumn("Source")
        },
        use_container_width=True
    )


    # --- DEEP DIVE SECTION ---

    if selection["selection"]["rows"]:
        try:
            selected_index = selection["selection"]["rows"][0]

            article_details = filtered_df.iloc[selected_index]


            with st.expander("Deep Dive: Selected Article", expanded=True):
                st.markdown(f"**Full Summary:** {article_details['summary']}")
                st.markdown(f"**Sentiment Score:** {article_details['sentiment']:.2f}")


                if 'highlights' in article_details and article_details['highlights']:
                    st.markdown("**Key Highlights:**")
                    l = ast.literal_eval(str(article_details['highlights']))
                
                    for highlight in l:
                        st.markdown(f"- *{highlight}*")

                st.markdown(f"**Source URL:** [Link]({article_details['url']})")
        except (IndexError, KeyError):

            st.warning("Please re-select a row from the current view to see details.")

if __name__ == "__main__":
    init_app()