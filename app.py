import streamlit as st
import pandas as pd

st.set_page_config(layout="wide")

# Load product data
@st.cache_data
def load_data():
    return pd.read_excel("Price List_Pair_Single.xlsx") 

df = load_data()

# Sidebar Filters
st.sidebar.header("Filter Products")
brands = st.sidebar.multiselect("Brand", df["Brand"].dropna().unique())
price_min, price_max = int(df["Price"].min()), int(df["Price"].max())
price_range = st.sidebar.slider("Price Range", min_value=price_min, max_value=price_max, value=(price_min, price_max))
gender = st.sidebar.multiselect("Gender", df["Gender"].dropna().unique())
movement = st.sidebar.multiselect("Movement", df["Movement"].dropna().unique())

# Filter logic
filtered_df = df[
    (df["Price"] >= price_range[0]) & (df["Price"] <= price_range[1])
]
if brands:
    filtered_df = filtered_df[filtered_df["Brand"].isin(brands)]
if gender:
    filtered_df = filtered_df[filtered_df["Gender"].isin(gender)]
if movement:
    filtered_df = filtered_df[filtered_df["Movement"].isin(movement)]

# Display products
st.markdown(f"### Showing {len(filtered_df)} Products")
for _, row in filtered_df.iterrows():
    cols = st.columns([1, 3])
    with cols[0]:
        st.image(row["ImageURL"], width=100)
    with cols[1]:
        st.markdown(f"**{row['Product Name']}**")
        st.markdown(f"Brand: {row['Brand']} | Price: ₹{row['Price']} | Ratings: {row.get('Ratings', 'N/A')}")
        if row.get("URL"):
            st.markdown(f"[View Product]({row['URL']})")
    st.markdown("---")
