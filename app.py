import streamlit as st
import pandas as pd

# Load data
@st.cache_data
def load_data():
    try:
        df = pd.read_excel("sourcefile.xlsx")
        return df
    except FileNotFoundError:
        st.error("Error: 'sourcefile.xlsx' not found. Please make sure the file is in the same directory as the script.")
        return None  # Return None to indicate an error

# Main function
def main():
    df = load_data()

    if df is None:
        return  # Stop execution if the data file wasn't found

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
    if 'Price' in df.columns:  # Check if 'Price' column exists
        min_price = int(df['Price'].min())
        max_price = int(df['Price'].max())
        price_range = st.sidebar.slider("Price Range", min_price, max_price, (min_price, max_price))
    else:
        st.sidebar.error("'Price' column not found in dataset.")
        price_range = (0, 0)  # Or some default value

    # Apply filters
    filtered_df = df.copy()
    if selected_brand != "All":
        filtered_df = filtered_df[filtered_df['Brand'] == selected_brand]

    if 'Price' in df.columns:  # Check again before filtering
        filtered_df = filtered_df[(filtered_df['Price'] >= price_range[0]) & (filtered_df['Price'] <= price_range[1])]

    # Display results
    st.title("🛍️ Product Selector")

    # Clean column names
    df.columns = df.columns.str.strip()

    if filtered_df.empty:
        st.warning("No products found with selected filters.")
    else:
        for _, row in filtered_df.iterrows():
            col1, col2 = st.columns([1, 2])  # Create two columns with a 1:2 ratio

            with col1:
                if 'ImageURL' in row and pd.notna(row['ImageURL']):  # Check for column and non-null value
                    st.image(row['ImageURL'], width=200)
                else:
                    st.write("Image not available")  # Handle missing images

            with col2:
                st.subheader(f"{row['Product Name']} - ₹{int(row['Price'])}")
                st.write(f"**Brand:** {row['Brand']}")
                st.write(f"**Model Number:** {row['Model Number']}")
                st.write(f"**Rating:** {row['Rating(out of 5)']}/5")
                st.write(f"**Discount:** {row['Discount (%)']}%")
            st.markdown("---")

if __name__ == "__main__":
    main()
