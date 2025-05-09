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
            continue  # Skip identifier

        unique_vals = sorted(df[col].dropna().astype(str).unique())

        # Numeric column
        if pd.api.types.is_numeric_dtype(df[col]):
            min_val, max_val = int(df[col].min()), int(df[col].max())
            selected_range = st.sidebar.slider(f"{col}", min_val, max_val, (min_val, max_val))
            filtered_df = filtered_df[filtered_df[col].between(*selected_range)]

        # YES/NO columns
        elif set(unique_vals).issubset({"YES", "NO"}):
            if st.sidebar.checkbox(f"Only with {col}", value=False):
                filtered_df = filtered_df[filtered_df[col] == "YES"]

        # Categorical dropdown with "All"
        elif len(unique_vals) <= 10:
            options = ["All"] + unique_vals
            selected = st.sidebar.selectbox(f"{col}", options=options)
            if selected != "All":
                filtered_df = filtered_df[filtered_df[col].astype(str) == selected]

        # Longer dropdown fallback
        else:
            options = ["All"] + unique_vals
            selected = st.sidebar.selectbox(f"{col}", options=options)
            if selected != "All":
                filtered_df = filtered_df[filtered_df[col].astype(str) == selected]

    return filtered_df

# ---- Main App ----
def main():
    st.set_page_config(page_title="Sameer ka Dhanda", layout="wide")
    df = load_data()
    if df is None:
        return

    st.title("🩺 Titan Audiology Product Portal")

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

    # ---- Product Display: 2-column styled card layout ----
    for i in range(0, len(paginated_df), 2):
        cols = st.columns(2)
        for j in range(2):
            if i + j < len(paginated_df):
                row = paginated_df.iloc[i + j]
                with cols[j]:
                    st.markdown(
                        f"""
                        <div style="
                            border: 1px solid #ccc;
                            border-radius: 10px;
                            padding: 20px;
                            margin-bottom: 10px;
                            background-color: #f9f9f9;
                            box-shadow: 2px 2px 10px rgba(0,0,0,0.05);
                        ">
                            <h4 style="margin-bottom: 10px;">{row['Model Name']}</h4>
                            <p>💰 <strong>Price:</strong> ₹{row['Price']}</p>
                            <p><strong>Quantity:</strong> {row['Quantity']}</p>
                            <p><strong>Degree of loss:</strong> {row['Degree of loss']}</p>
                            <p><strong>Channels:</strong> {row['Channels']}</p>
                    """,
                        unsafe_allow_html=True
                    )

                    # YES/NO or other features
                    for col in df.columns:
                        if col not in ["Model Name", "Price", "Quantity", "Degree of loss", "Channels"]:
                            value = str(row[col]).strip().upper()
                            if value == "YES":
                                st.markdown(f"<p style='color:green;'>✅ {col}</p>", unsafe_allow_html=True)
                            elif value == "NO":
                                st.markdown(f"<p style='color:red;'>❌ {col}</p>", unsafe_allow_html=True)
                            else:
                                st.markdown(f"<p><strong>{col}:</strong> {row[col]}</p>", unsafe_allow_html=True)

                    st.markdown("</div>", unsafe_allow_html=True)

if __name__ == "__main__":
    main()
