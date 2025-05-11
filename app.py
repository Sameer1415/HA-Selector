import streamlit as st
import pandas as pd

# ---- Load data ----
@st.cache_data
def load_data():
    try:
        df = pd.read_excel("sourcedata.xlsx")
        df.columns = df.columns.str.strip()

        # Merge duplicate features
        if "Augmented Focus.1" in df.columns and "Augmented Focus" in df.columns:
            df["Augmented Focus"] = df["Augmented Focus"].combine_first(df["Augmented Focus.1"])
            df.drop(columns=["Augmented Focus.1"], inplace=True)

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
        label = "REQUIREMENT" if col.upper() == "DEGREE OF LOSS" else col

        # ---- Quantity as horizontal radio ----
        if col.upper() == "QUANTITY":
            selected = st.sidebar.radio("Quantity", options=unique_vals, horizontal=True)
            filtered_df = filtered_df[filtered_df[col] == selected]

        # ---- Numeric sliders ----
        elif col.upper() == "PRICE":
            price_bucket = st.sidebar.radio(
                "Price Range",
                options=["30,000 – 1,00,000", "1,00,000 – 3,00,000", "3,00,000+"],
                horizontal=False
            )
            if price_bucket == "30K – 1 Lakh":
                filtered_df = filtered_df[(df[col] >= 30000) & (df[col] < 100000)]
            elif price_bucket == "1 Lakh – 3 Lakhs":
                filtered_df = filtered_df[(df[col] >= 100000) & (df[col] < 300000)]
            else:
                filtered_df = filtered_df[df[col] >= 300000]

        # ---- YES/NO checkboxes ----
        elif set(unique_vals).issubset({"YES", "NO"}):
            if st.sidebar.checkbox(label, value=False):
                filtered_df = filtered_df[filtered_df[col] == "YES"]

        # ---- Dropdown for short categories (without "All") ----
        elif len(unique_vals) <= 10:
            selected = st.sidebar.selectbox(label, options=unique_vals)
            filtered_df = filtered_df[filtered_df[col] == selected]

        # ---- Long category fallback ----
        else:
            selected = st.sidebar.selectbox(label, options=unique_vals)
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
    df["Model Group"] = df["Model Name"].str.extract(r"^(\w+)", expand=False).str.upper()
    model_groups = sorted(df["Model Group"].dropna().unique())
    
    st.markdown("## Select Model Group")
    group_cols = st.columns(len(model_groups))
    
    for i, group in enumerate(model_groups):
        if group_cols[i].button(group):
            st.session_state.selected_group = group
            st.session_state.selected_model = None  # Reset model
    
    # Default: pick first group if not already selected
    if "selected_group" not in st.session_state:
        st.session_state.selected_group = model_groups[0]
    
    group_df = df[df["Model Group"] == st.session_state.selected_group]
    model_names = sorted(group_df["Model Name"].dropna().unique())
    
    st.markdown(f"### Models in {st.session_state.selected_group}")
    model_cols = st.columns(len(model_names))
    
    for i, model in enumerate(model_names):
        if model_cols[i].button(model):
            st.session_state.selected_model = model
    
    # Default: pick first model
    if "selected_model" not in st.session_state or st.session_state.selected_model not in model_names:
        st.session_state.selected_model = model_names[0]
    
    # Display the selected model card
    model_row = group_df[group_df["Model Name"] == st.session_state.selected_model].iloc[0]
    
    st.markdown(
        f"""
        <div style="border:1px solid #ccc; padding:20px; border-radius:10px; background-color:#f9f9f9; margin-top: 20px;">
            <h4>{model_row['Model Name']}</h4>
            <p><strong>💰 Price:</strong> ₹{model_row['Price']}</p>
            <p><strong>Quantity:</strong> {model_row['Quantity']}</p>
            <p><strong>Requirement:</strong> {model_row['Degree of loss']}</p>
            <p><strong>Channels:</strong> {model_row['Channels']}</p>
        </div>
        """,
        unsafe_allow_html=True
    )
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
