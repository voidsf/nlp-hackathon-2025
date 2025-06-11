

# Example usage

data = {"id": [1,2,3],
        "title": ["Xbox game pass", "Xbox pass", "game time"]}

df = pd.DataFrame(data)

common_df = get_common_keywords_df(df)
print(common_df)