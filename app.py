import streamlit as st
import pandas as pd

# ---- Load data ----
@st.cache_data
def load_data():
    try:
        df = pd.read_excel("sourcefile.xlsx")
        df.columns = df.columns.str.strip()
        df["Price"] = pd.to_numeric(df["Price"].astype(str).str.replace(",", ""), errors="coerce").fillna(0).astype(int)
        return df
    except FileNotFoundError:
        st.error("❌ Error: 'sourcefile.xlsx' not found.")
        return None

# ---- Sidebar Filter Logic ----
def render_sidebar_filters(df):
    st.sidebar.header("🎛️ Filters")
    filtered_df = df.copy()

    for col in df.columns:
        if col.lower() == "model name":
            continue  # Skip product identifier

        unique_vals = sorted(df[col].dropna().astype(str).unique())

        # Numeric Filters (e.g., Price)
        if pd.api.types.is_numeric_dtype(df[col]):
            min_val, max_val = int(df[col].min()), int(df[col].max())
            selected_range = st.sidebar.slider(f"{col}", min_val, max_val, (min_val, max_val))
            filtered_df = filtered_df[filtered_df[col].between(*selected_range)]

        # YES/NO columns
        elif set(unique_vals).issubset({"YES", "NO"}):
            if st.sidebar.checkbox(f"Only with {col}", value=False):
                filtered_df = filtered_df[filtered_df[col] == "YES"]

        # Short Categorical Columns (dropdown with All)
        elif len(unique_vals) <= 10:
            options = ["All"] + unique_vals
            selected = st.sidebar.selectbox(f"{col}", options=options, index=0)
            if selected != "All":
                filtered_df = filtered_df[filtered_df[col].astype(str) == selected]

        # Long list → fallback to selectbox
        else:
            options = ["All"] + unique_vals
            selected = st.sidebar.selectbox(f"{col}", options=options, index=0)
            if selected != "All":
                filtered_df = filtered_df[filtered_df[col].astype(str) == selected]

    return filtered_df

# ---- Main App ----
def main():
    st.set_page_config(page_title="HA Selector", layout="wide")
    df = load_data()
    if df is None:
        return

    st.title("🩺 Titan Audiology Product Portal")

    # Apply dynamic sidebar filters
    filtered_df = render_sidebar_filters(df)

    # Pagination
    items_per_page = 12
    total_pages = (len(filtered_df) - 1) // items_per_page + 1 if len(filtered_df) > 0 else 0

    if total_pages > 0:
        page = st.sidebar.number_input("📄 Page", 1, total_pages, 1)
        start_idx = (page - 1) * items_per_page
        end_idx = start_idx + items_per_page
        paginated_df = filtered_df.iloc[start_idx:end_idx]
    else:
        st.warning("No products match your filters.")
        paginated_df = pd.DataFrame()

    # Display product cards in 3-column layout
    for i in range(0, len(paginated_df), 3):
        cols = st.columns(3)
        for j in range(3):
            if i + j < len(paginated_df):
                row = paginated_df.iloc[i + j]
                with cols[j]:
                    st.markdown(f"### {row['Model Name']}")
                    st.write(f"💰 **Price:** ₹{row['Price']}")
                    for col in df.columns:
                        if col not in ["Model Name", "Price"]:
                            value = row[col]
                            value_str = str(value).strip().upper()
                            if value_str == "YES":
                                st.write(f"✅ **{col}**")
                            elif value_str == "NO":
                                st.write(f"❌ **{col}**")
                            else:
                                st.write(f"**{col}:** {value}")

    st.markdown("---")

if __name__ == "__main__":
    main()
