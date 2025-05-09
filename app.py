import streamlit as st
import pandas as pd

# ---- Load data ----
@st.cache_data
def load_data():
    try:
        df = pd.read_excel("sourcefile.xlsx")
        df.columns = df.columns.str.strip()  # Clean column names
        df["Price"] = pd.to_numeric(df["Price"].astype(str).str.replace(",", ""), errors="coerce").fillna(0).astype(int)
        return df
    except FileNotFoundError:
        st.error("Error: 'sourcefile.xlsx' not found.")
        return None


# ---- Main App ----
def main():
    st.set_page_config(page_title="Sameer ka Dhanda", layout="wide")
    df = load_data()
    if df is None:
        return

    st.title("🩺 Titan Audiology Product Portal")

    # Sidebar Filters
    st.sidebar.header("🎛️ Filters")

    # Degree of loss
    loss_options = sorted(df["Degree of loss"].dropna().unique())
    selected_loss = st.sidebar.multiselect("Degree of Loss", options=loss_options, default=loss_options)

    # Price
    min_price, max_price = df["Price"].min(), df["Price"].max()
    selected_price = st.sidebar.slider("Price Range (₹)", min_price, max_price, (min_price, max_price))

    # Features (Checkbox filters)
    features = ["Bluetooth", "Echo shield", "Tinnitus Manager", "Augmented Focus", "Android and ios Streaming"]
    selected_features = {}
    for feature in features:
        selected_features[feature] = st.sidebar.checkbox(f"Only with {feature}", value=False)

    # Filter the data
    filtered_df = df[
        df["Degree of loss"].isin(selected_loss) &
        df["Price"].between(*selected_price)
    ]
    for feat, val in selected_features.items():
        if val:
            filtered_df = filtered_df[filtered_df[feat] == "YES"]

    # Pagination
    items_per_page = 12
    total_pages = (len(filtered_df) - 1) // items_per_page + 1
    page = st.sidebar.number_input("Page", 1, total_pages, 1)

    # Display cards
    start_idx = (page - 1) * items_per_page
    end_idx = start_idx + items_per_page
    for i in range(start_idx, min(end_idx, len(filtered_df)), 3):
        cols = st.columns(3)
        for j in range(3):
            if i + j < len(filtered_df):
                row = filtered_df.iloc[i + j]
                with cols[j]:
                    st.markdown(f"### {row['Model Name']}")
                    st.write(f"💰 **Price:** ₹{row['Price']}")
                    st.write(f"🧠 **Degree of Loss:** {row['Degree of loss']}")
                    st.write(f"🎧 **Channels:** {row['Channels']}")
                    for feat in features:
                        emoji = "✅" if row[feat] == "YES" else "❌"
                        st.write(f"{emoji} {feat}")

    st.markdown("---")

if __name__ == "__main__":
    main()
