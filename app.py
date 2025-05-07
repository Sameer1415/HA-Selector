import streamlit as st
import pandas as pd

# Load data
@st.cache_data
def load_data():
    df = pd.read_excel("sourcefile.xlsx")
    return df

df = load_data()

# Sidebar filters
st.sidebar.header("Filter Products")

# Brand filter
if 'Brand' in df.columns:
    brand_options = df['Brand'].dropna().unique().tolist()
    selected_brand = st.sidebar.selectbox("Brand", ["All"] + sorted(brand_options))
else:
    st.sidebar.error("'Brand' column not found in dataset.")
    selected_brand = "All"

# Price filter
min_price = int(df['Price'].min())
max_price = int(df['Price'].max())
price_range = st.sidebar.slider("Price Range", min_price, max_price, (min_price, max_price))

# Apply filters
filtered_df = df.copy()
if selected_brand != "All":
    filtered_df = filtered_df[filtered_df['Brand'] == selected_brand]

filtered_df = filtered_df[(filtered_df['Price'] >= price_range[0]) & (filtered_df['Price'] <= price_range[1])]

# Display results
st.title("🛍️ Product Selector")

# Clean column names
df.columns = df.columns.str.strip()

# Show filtered results
if filtered_df.empty:
    st.warning("No products found with selected filters.")
else:
    for _, row in filtered_df.iterrows():
        st.subheader(f"{row['Product Name']} - ₹{int(row['Price'])}")
        st.write(f"**Brand:** {row['Brand']}")
        st.write(f"**Model Number:** {row['Model Number']}")
        st.write(f"**Rating:** {row['Rating(out of 5)']}/5")
        st.write(f"**Discount:** {row['Discount (%)']}%")
        
        # Display image from 'ImageURL' column
        image_url = row['ImageURL']
        if pd.notna(image_url):
            st.image(image_url, width=200)
        else:
            st.warning("No image available for this product.")
        
        st.markdown("---")
