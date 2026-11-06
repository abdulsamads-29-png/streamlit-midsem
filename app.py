import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

st.set_page_config(page_title="IMDb Dashboard", layout="wide")

st.title("🎬 IMDb Top 250 Movies Dashboard")

# Q1: Dataset Loading
df = pd.read_csv("ToP 250 movies on imdb in 2026 (1) - Copy.csv")

st.success("Dataset Loaded Successfully!")

st.subheader("First 10 Records")
st.dataframe(df.head(10))

st.write("Dataset Shape:", df.shape)
st.write("Column Names:", list(df.columns))
st.write("Data Types:")
st.write(df.dtypes)
st.write("Missing Values:")
st.write(df.isnull().sum())

# Convert numeric columns
df["averageRating"] = pd.to_numeric(df["averageRating"], errors="coerce")
df["numVotes"] = pd.to_numeric(df["numVotes"], errors="coerce")
df["grossWorldwide"] = pd.to_numeric(
    df["grossWorldwide"].astype(str).str.replace(r"[$,]", "", regex=True),
    errors="coerce"
)

st.divider()

# Q2: KPI Metrics
st.header("Movie Analytics Dashboard")

c1, c2, c3, c4 = st.columns(4)

c1.metric("Total Movies", len(df))
c2.metric("Average Rating", round(df["averageRating"].mean(), 2))
c3.metric("Highest Rating", df["averageRating"].max())
c4.metric("Total Votes", f"{df['numVotes'].sum():,.0f}")

st.divider()

# Q3 and Q4: Visualizations and Tabs
st.header("Movie Visualizations")

tab1, tab2, tab3 = st.tabs(
    ["Genre Analysis", "Rating Analysis", "Gross Collection"]
)

with tab1:
    st.subheader("Movies by Genre")
    genres = df["genres"].dropna().str.split(",").explode().str.strip()
    st.bar_chart(genres.value_counts())

with tab2:
    st.subheader("IMDb Rating Distribution")

    fig, ax = plt.subplots(figsize=(5, 3))
    ax.hist(df["averageRating"].dropna(), bins=10)
    ax.set_xlabel("Rating")
    ax.set_ylabel("Number of Movies")
    st.pyplot(fig)
    plt.close(fig)

    st.subheader("Rating vs Votes")
    st.scatter_chart(df, x="averageRating", y="numVotes")

with tab3:
    st.subheader("Top 10 Movies by Worldwide Gross")

    top10 = df.nlargest(10, "grossWorldwide")

    st.bar_chart(top10.set_index("primaryTitle")["grossWorldwide"])
    st.dataframe(top10)

with st.expander("Dataset Information"):
    st.write("Total Rows:", df.shape[0])
    st.write("Total Columns:", df.shape[1])
    st.write("Available Columns:", df.columns.tolist())

st.info("Explore the IMDb Movie Dashboard.")

st.divider()

# Q5: Interactive Movie Explorer
st.header("Interactive Movie Explorer")

if st.button("Reset Filters"):
    st.session_state.clear()
    st.rerun()

filtered = df.copy()

genres = sorted(genres.dropna().unique().tolist())

genre = st.selectbox("Select Genre", ["All"] + genres)

if genre != "All":
    filtered = filtered[
        filtered["genres"].str.contains(genre, na=False)
    ]

countries = sorted(
    df["countriesOfOrigin"].dropna()
    .str.split(",").explode().str.strip().unique()
)

country = st.multiselect("Select Countries", countries)

if country:
    filtered = filtered[
        filtered["countriesOfOrigin"].fillna("").apply(
            lambda x: any(c in [i.strip() for i in x.split(",")] for c in country)
        )
    ]

rating = st.slider("IMDb Rating", 0.0, 10.0, (0.0, 10.0))

filtered = filtered[
    filtered["averageRating"].between(rating[0], rating[1])
]

votes = st.number_input("Minimum Votes", min_value=0, value=0)

filtered = filtered[filtered["numVotes"] >= votes]

search = st.text_input("Search Movie")

filtered = filtered[
    filtered["primaryTitle"].str.contains(search, case=False, na=False)
]

sort = st.radio("Sort Rating", ["Ascending", "Descending"])

filtered = filtered.sort_values(
    "averageRating", ascending=(sort == "Ascending")
)

st.metric("Movies Found", len(filtered))
st.dataframe(filtered, use_container_width=True)

# Q6: Session State and Form
st.divider()
st.header("Movie Search Form")

if "selected_movie" not in st.session_state:
    st.session_state.selected_movie = None

with st.form("movie_form"):

    movie = st.text_input("Movie Title")

    preferred_genre = st.selectbox(
        "Preferred Genre",
        ["All"] + genres
    )

    min_rating = st.slider("Minimum Rating", 0.0, 10.0, 7.0)

    submit = st.form_submit_button("Search Movie")

if submit:

    result = df[
        (df["primaryTitle"].str.contains(movie, case=False, na=False)) &
        (df["averageRating"] >= min_rating)
    ]

    if preferred_genre != "All":
        result = result[
            result["genres"].str.contains(preferred_genre, na=False)
        ]

    if not result.empty:
        st.session_state.selected_movie = result.iloc[0]
        st.success("Movie Found!")
    else:
        st.session_state.selected_movie = None
        st.info("No Matching Movie Found.")

if st.session_state.selected_movie is not None:

    m = st.session_state.selected_movie

    st.subheader("Selected Movie Information")

    st.write("Movie:", m["primaryTitle"])
    st.write("Genre:", m["genres"])
    st.write("Rating:", m["averageRating"])
    st.write("Votes:", m["numVotes"])

st.divider()
st.success("Dashboard Completed Successfully!")