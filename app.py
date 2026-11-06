
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

st.set_page_config(layout="wide")

# Q1. Load Dataset
st.title("IMDb Movie Dashboard")

df = pd.read_csv("ToP 250 movies on imdb in 2026.csv")

# Detect movie title column
title_col = next(
    c for c in ["title", "originalTitle", "primaryTitle"]
    if c in df.columns
)

st.success("Dataset Loaded Successfully!")

st.dataframe(df.head(10))
st.write(df.shape)
st.write(df.dtypes)
st.write(df.isnull().sum())

# Q2. KPI Metrics
st.header("Movie Analytics")

c1, c2, c3, c4 = st.columns(4)

c1.metric("Movies", len(df))
c2.metric("Average Rating", round(df["averageRating"].mean(), 2))
c3.metric("Highest Rating", df["averageRating"].max())
c4.metric("Total Votes", int(df["numVotes"].sum()))

# Q3. Charts
st.header("Data Visualization")

tab1, tab2, tab3 = st.tabs(["Genre", "Rating", "Gross"])

with tab1:
    genres = df["genres"].str.split(",").explode()
    st.bar_chart(genres.value_counts())

with tab2:
    fig, ax = plt.subplots()
    ax.hist(df["averageRating"].dropna(), bins=10)
    st.pyplot(fig)
    plt.close(fig)

    fig, ax = plt.subplots()
    ax.scatter(df["averageRating"], df["numVotes"])
    st.pyplot(fig)
    plt.close(fig)

with tab3:
    top10 = df.nlargest(10, "grossWorldwide")
    st.bar_chart(top10.set_index(title_col)["grossWorldwide"])

# Q4. Layout
with st.expander("Dataset Information"):
    st.write(df.shape)
    st.write(df.columns.tolist())

st.divider()
st.info("Explore the dashboard")

# Q5. Movie Explorer
st.header("Movie Explorer")

genre = st.selectbox(
    "Genre",
    ["All"] + sorted(df["genres"].dropna().str.split(",").explode().unique())
)

country_col = next(
    (c for c in ["countriesOrigin", "countries_origin", "country", "countries"]
     if c in df.columns),
    None
)

if country_col:
    country = st.multiselect(
        "Country", sorted(df[country_col].dropna().unique())
    )
else:
    country = []

rating = st.slider("Minimum Rating", 0.0, 10.0, 7.0)
votes = st.number_input("Minimum Votes", min_value=0)
search = st.text_input("Search Movie")
sort = st.radio("Sort", ["Ascending", "Descending"])

filtered = df.copy()

if genre != "All":
    filtered = filtered[
        filtered["genres"].str.contains(genre, na=False)
    ]

if country:
    filtered = filtered[filtered[country_col].isin(country)]

filtered = filtered[
    (filtered["averageRating"] >= rating) &
    (filtered["numVotes"] >= votes)
]

filtered = filtered[
    filtered[title_col].str.contains(search, case=False, na=False)
]

filtered = filtered.sort_values(
    "averageRating",
    ascending=(sort == "Ascending")
)

st.write("Movies Found:", len(filtered))
st.dataframe(filtered)

if st.button("Reset"):
    st.rerun()

# Q6. Session State and Form
if "movie" not in st.session_state:
    st.session_state.movie = None

with st.form("movie_form"):
    title = st.text_input("Movie Title")
    preferred_genre = st.selectbox(
        "Preferred Genre",
        ["All"] + sorted(
            df["genres"].dropna().str.split(",").explode().unique()
        )
    )
    min_rating = st.slider("Minimum Rating", 0.0, 10.0, 7.0)
    submit = st.form_submit_button("Search")

if submit:
    result = df[
        df[title_col].str.contains(title, case=False, na=False) &
        (df["averageRating"] >= min_rating)
    ]

    if preferred_genre != "All":
        result = result[
            result["genres"].str.contains(preferred_genre, na=False)
        ]

    st.session_state.movie = (
        result.iloc[0].to_dict() if not result.empty else None
    )

if st.session_state.movie:
    st.success("Movie Found!")
    st.write(st.session_state.movie)
elif submit:
    st.info("Movie Not Found!")
