import streamlit as st
import pandas as pd

# Load data
@st.cache_data
def load_data():
    df = pd.read_excel('top100_men_filled.xlsx')
    return df

df = load_data()

st.title("🛍️ Product Portal - Top 100 Men Products")

# Sidebar filters
st.sidebar.header("Filter Products")

# Filter: Brand
if 'Brand' in df.columns:
    brands = st.sidebar.multiselect("Select Brand(s):", sorted(df['Brand'].dropna().unique()), default=None)
    if brands:
        df = df[df['Brand'].isin(brands)]

# Filter: Price
if 'Price' in df.columns:
    min_price, max_price = int(df['Price'].min()), int(df['Price'].max())
    price_range = st.sidebar.slider("Price Range", min_price, max_price, (min_price, max_price))
    df = df[(df['Price'] >= price_range[0]) & (df['Price'] <= price_range[1])]

# Filter: Rating
if 'Rating' in df.columns:
    min_rating, max_rating = float(df['Rating'].min()), float(df['Rating'].max())
    rating_filter = st.sidebar.slider("Minimum Rating", min_rating, max_rating, min_rating)
    df = df[df['Rating'] >= rating_filter]

# Filter: Search by name
if 'Product Name' in df.columns:
    search_term = st.sidebar.text_input("Search by product name")
    if search_term:
        df = df[df['Product Name'].str.contains(search_term, case=False)]

# Display products
st.subheader(f"Showing {len(df)} product(s):")

if df.empty:
    st.warning("No products match your filters.")
else:
    for i, row in df.iterrows():
        st.markdown("---")
        col1, col2 = st.columns([1, 3])
        with col1:
            if 'Image' in df.columns and pd.notna(row['Image']):
                st.image(row['Image'], width=120)
        with col2:
            st.markdown(f"### {row.get('Product Name', 'Unnamed Product')}")
            st.markdown(f"**Brand**: {row.get('Brand', 'N/A')}")
            st.markdown(f"**Price**: ₹{row.get('Price', 'N/A')}")
            st.markdown(f"**Rating**: {row.get('Rating', 'N/A')} ⭐")

