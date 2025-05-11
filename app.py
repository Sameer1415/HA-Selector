import streamlit as st
import pandas as pd

# ---- Load data ----
@st.cache_data
def load_data():
    try:
        df = pd.read_excel("sourcefile")
        df.columns = df.columns.str.strip()

        # Convert Price
        df["Price"] = pd.to_numeric(
            df["Price"].astype(str).str.replace(",", ""), errors="coerce"
        ).fillna(0).astype(int)

        # Standardize string values to uppercase
        for col in df.select_dtypes(include="object").columns:
            df[col] = df[col].astype(str).str.strip().str.upper()

        return df
    except FileNotFoundError:
        st.error("❌ Error: 'sourcefile.xlsx' not found.")
        return None

# ---- Sidebar Filter Logic ----
def render_sidebar_filters(df):
    st.sidebar.header("🎛️ Filters")
    filtered_df = df.copy()

    # Map uppercase to actual DataFrame column names
    df_columns_upper = {col.upper(): col for col in df.columns}

    preferred_order = ["QUANTITY", "DEGREE OF LOSS", "CHANNELS"]
    ordered_cols = [df_columns_upper[col] for col in preferred_order if col in df_columns_upper]
    other_columns = [col for col in df.columns if col not in ordered_cols and col.upper() != "MODEL NAME"]
    filter_order = ordered_cols + other_columns

    for col in filter_order:
        unique_vals = sorted(df[col].dropna().astype(str).unique())

        if pd.api.types.is_numeric_dtype(df[col]):
            min_val, max_val = int(df[col].min()), int(df[col].max())
            selected_range = st.sidebar.slider(f"{col}", min_val, max_val, (min_val, max_val))
            filtered_df = filtered_df[filtered_df[col].between(*selected_range)]

        elif set(unique_vals).issubset({"YES", "NO"}):
            if st.sidebar.checkbox(f"{col}", value=False):
                filtered_df = filtered_df[filtered_df[col] == "YES"]

        elif len(unique_vals) <= 10:
            options = ["All"] + unique_vals
            selected = st.sidebar.selectbox(f"{col}", options=options)
            if selected != "All":
                filtered_df = filtered_df[filtered_df[col] == selected]

        else:
            options = ["All"] + unique_vals
            selected = st.sidebar.selectbox(f"{col}", options=options)
            if selected != "All":
                filtered_df = filtered_df[filtered_df[col] == selected]

    return filtered_df


# ---- Main App ----
def main():
    st.set_page_config(page_title="HA Selector", layout="wide")
    df = load_data()
    if df is None:
        return

    st.title("Titan HA Products")
    filtered_df = render_sidebar_filters(df)

    # Pagination setup
    items_per_page = 8
    total_pages = (len(filtered_df) - 1) // items_per_page + 1 if len(filtered_df) > 0 else 0

    if "current_page" not in st.session_state:
        st.session_state.current_page = 1

    if st.session_state.current_page > total_pages:
        st.session_state.current_page = total_pages
    if st.session_state.current_page < 1:
        st.session_state.current_page = 1

    start_idx = (st.session_state.current_page - 1) * items_per_page
    end_idx = start_idx + items_per_page
    paginated_df = filtered_df.iloc[start_idx:end_idx]

    if paginated_df.empty:
        st.warning("No products match your filters.")
        return

    # ---- Product Display ----
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

    # ---- Flipkart-style Pagination ----
    if total_pages > 1:
        # st.markdown("### 📄 Pages:")
        nav_cols = st.columns(min(total_pages + 2, 10))  # Show up to 7 numbered buttons

        if nav_cols[0].button("⬅️ Prev", disabled=(st.session_state.current_page == 1)):
            st.session_state.current_page -= 1

        for i in range(1, min(total_pages + 1, 8)):
            if nav_cols[i].button(str(i), disabled=(i == st.session_state.current_page)):
                st.session_state.current_page = i

        if nav_cols[-1].button("Next ➡️", disabled=(st.session_state.current_page == total_pages)):
            st.session_state.current_page += 1

if __name__ == "__main__":
    main()
