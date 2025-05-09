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

    # Degree of Loss
    degree_options = sorted(df["Degree of loss"].dropna().unique())
    selected_degrees = st.sidebar.multiselect("Degree of Loss", options=degree_options, default=degree_options)

    # Price Filter
    min_price, max_price = int(df["Price"].min()), int(df["Price"].max())
    selected_price = st.sidebar.slider("Price Range (₹)", min_price, max_price, (min_price, max_price))

    # Feature Filters
    features = ["Bluetooth", "Echo shield", "Tinnitus Manager", "Augmented Focus", "Android and ios Streaming"]
    selected_features = {}
    for feat in features:
        selected_features[feat] = st.sidebar.checkbox(f"Only with {feat}", value=False)

    # ---- Apply filters ----
    filtered_df = df[
        df["Degree of loss"].isin(selected_degrees) &
        df["Price"].between(*selected_price)
    ]

    for feat, checked in selected_features.items():
        if checked:
            filtered_df = filtered_df[filtered_df[feat] == "YES"]

    # ---- Pagination ----
    items_per_page = 12
    total_pages = (len(filtered_df) - 1) // items_per_page + 1 if len(filtered_df) > 0 else 0

    if total_pages > 0:
        page = st.sidebar.number_input("Page", 1, total_pages, 1)
        start_idx = (page - 1) * items_per_page
        end_idx = start_idx + items_per_page
        paginated_df = filtered_df.iloc[start_idx:end_idx]
    else:
        st.warning("No products match your filters.")
        paginated_df = pd.DataFrame()

    # ---- Display Product Cards ----
    for i in range(0, len(paginated_df), 3):
        cols = st.columns(3)
        for j in range(3):
            if i + j < len(paginated_df):
                row = paginated_df.iloc[i + j]
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
