import streamlit as st
import pandas as pd

# Load data
@st.cache_data
def load_data():
    df = pd.read_excel("sourcefile.xlsx")
    return df

df = load_data()

st.title("🛍️ Men's Watches Portal")

# Sidebar filters
st.sidebar.header("Filter Products")

# Filter: Brand
brands = st.sidebar.multiselect("Select Brand(s):", sorted(df['Brand'].dropna().unique()))
if brands:
    df = df[df['Brand'].isin(brands)]

# Filter: Price
min_price, max_price = int(df['Price'].min()), int(df['Price'].max())
price_range = st.sidebar.slider("Price Range", min_price, max_price, (min_price, max_price))
df = df[(df['Price'] >= price_range[0]) & (df['Price'] <= price_range[1])]

# Filter: Rating
if 'Rating(out of 5)' in df.columns:
    min_rating, max_rating = float(df['Rating(out of 5)'].min()), float(df['Rating(out of 5)'].max())
    rating_filter = st.sidebar.slider("Minimum Rating", min_rating, max_rating, min_rating)
    df = df[df['Rating(out of 5)'] >= rating_filter]

# Filter: Search by product name
search_term = st.sidebar.text_input("Search by product name")
if search_term:
    df = df[df['Product Name'].str.contains(search_term, case=False)]

# Display products
st.subheader(f"Showing {len(df)} product(s):")

if df.empty:
    st.warning("No products match your filters.")
else:
    for _, row in df.iterrows():
        st.markdown("---")
        col1, col2 = st.columns([1, 3])
        with col1:
            if pd.notna(row['URL']):
                st.image(row['URL'], width=120)
        with col2:
            st.markdown(f"### {row['Product Name']}")
            st.markdown(f"**Brand**: {row['Brand']}")
            st.markdown(f"**Model**: {row['Model Number']}")
            st.markdown(f"**Price**: ₹{row['Price']}")
            st.markdown(f"**Rating**: {row['Rating(out of 5)']} ⭐")
