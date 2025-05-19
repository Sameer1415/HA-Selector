import streamlit as pd
import streamlit as st

# ---- Load Data ----
@st.cache_data
def load_data():
    """
    Loads data from 'sourcedata.xlsx', handles errors, and preprocesses the data.
    """
    try:
        df = pd.read_excel("sourcedata.xlsx")
        df.columns = df.columns.str.strip()

        # Handle the case where both 'Augmented Focus.1' and 'Augmented Focus' exist
        if "Augmented Focus.1" in df.columns and "Augmented Focus" in df.columns:
            df["Augmented Focus"] = df["Augmented Focus"].combine_first(df["Augmented Focus.1"])
            df.drop(columns=["Augmented Focus.1"], inplace=True)

        # Convert 'Price' to numeric, handling commas and missing values
        df["Price"] = pd.to_numeric(df["Price"].astype(str).str.replace(",", ""), errors="coerce").fillna(
            0).astype(int)

        # Convert object type columns to uppercase and strip whitespace
        for col in df.select_dtypes(include="object").columns:
            df[col] = df[col].astype(str).str.strip().str.upper()

        return df
    except FileNotFoundError:
        st.error("❌ Error: 'sourcedata.xlsx' not found.")
        return None

# ---- Sidebar Filters ----
def render_sidebar_filters(df):
    """
    Renders the sidebar filters and returns the filtered DataFrame.

    Args:
        df (pd.DataFrame): The input DataFrame.

    Returns:
        pd.DataFrame: The filtered DataFrame.
    """
    st.sidebar.header("🎛️ Filters")
    filtered_df = df.copy()

    df_columns_upper = {col.upper(): col for col in df.columns}
    preferred_order = ["QUANTITY", "DEGREE OF LOSS", "CHANNELS"]
    ordered_cols = [df_columns_upper[col] for col in preferred_order if col in df_columns_upper]
    other_columns = [col for col in df.columns if col not in ordered_cols and col.upper() != "MODEL NAME"]
    filter_order = ordered_cols + other_columns

    for col in filter_order:
        if col not in filtered_df.columns:
            continue

        unique_vals = sorted(filtered_df[col].dropna().astype(str).unique())
        label = "REQUIREMENT" if col.upper() == "DEGREE OF LOSS" else col

        if col.upper() == "QUANTITY":
            selected = st.sidebar.radio("Quantity", options=unique_vals, horizontal=True)
            filtered_df = filtered_df[filtered_df[col] == selected]

        elif col.upper() == "PRICE":
            price_bucket = st.sidebar.radio(
                "Price Range",
                options=["30,000 – 1,00,000", "1,00,000 – 3,00,000", "3,00,000+"],
            )
            if price_bucket == "30,000 – 1,00,000":
                filtered_df = filtered_df[(filtered_df[col] >= 30000) & (filtered_df[col] < 100000)]
            elif price_bucket == "1,00,000 – 3,00,000":
                filtered_df = filtered_df[(filtered_df[col] >= 100000) & (filtered_df[col] < 300000)]
            elif price_bucket == "30,000 – 1,00,000":
                filtered_df = filtered_df[filtered_df[col] >= 300000]

        elif col.upper() == "DEGREE OF LOSS":
            requirement_order = ["MILD", "MODERATE", "SEVERE", "PROFOUND"]
            selected = st.sidebar.selectbox("Requirement", options=requirement_order)
            filter_map = {
                "MILD": ["MILD", "MODERATE", "SEVERE", "PROFOUND"],
                "MODERATE": ["MODERATE", "SEVERE", "PROFOUND"],
                "SEVERE": ["SEVERE", "PROFOUND"],
                "PROFOUND": ["PROFOUND"]
            }
            filtered_df = filtered_df[filtered_df[col].isin(filter_map[selected])]

        elif set(unique_vals).issubset({"YES", "NO"}):
            if st.sidebar.checkbox(label, value=False):
                filtered_df = filtered_df[filtered_df[col] == "YES"]

        elif col.upper() == "CHANNELS":
            options = ["All"] + unique_vals
            selected = st.sidebar.selectbox(label, options=options)
            if selected != "All":
                filtered_df = filtered_df[filtered_df[col] == selected]

        else:
            selected = st.sidebar.selectbox(label, options=unique_vals)
            filtered_df = filtered_df[filtered_df[col] == selected]

    return filtered_df


# ---- Show Individual Model Card ----
def show_model_card(row):
    """
    Displays an individual model's information.

    Args:
        row (pd.Series): A row from the DataFrame representing a model.
    """
    st.markdown(f"### 📌 {row['Model Name']}")
    st.markdown(f"💰 **Price:** ₹{row['Price']:,}")
    st.markdown(f"🔢 **Channels:** {row.get('Channels', 'N/A')}")

    excluded = {"Model Name", "Price", "Channels", "Quantity", "Degree of loss", "Model Group"}
    for col in row.index:
        if col not in excluded:
            val = row[col]
            if str(val).upper() == "YES":
                icon = "✅"
            elif str(val).upper() == "NO":
                icon = "❌"
            else:
                icon = str(val)
            st.markdown(f"- **{col}**: {icon}")


# ---- Show comparison table ----
def show_comparison_table(models_df):
    """
    Displays a comparison table of model features.

    Args:
        models_df (pd.DataFrame): DataFrame containing the models to compare.
    """
    st.markdown("## 📊 Feature Comparison")

    # Handle empty DataFrame
    if models_df.empty:
        st.warning("No models to compare.")
        return

    comparison_cols = ["Channels", "Price"]
    other_cols = [col for col in models_df.columns if
                  col not in ["Model Name", "Quantity", "Degree of loss", "Model Group"] + comparison_cols]
    comparison_cols += other_cols

    comparison_data = pd.DataFrame(index=comparison_cols)

    for _, row in models_df.iterrows():
        values = []
        for col in comparison_cols:
            val = row.get(col, "")
            if pd.isna(val):  # Check for null values
                values.append("")
            elif str(val).upper() == "YES":
                values.append("✅")
            elif str(val).upper() == "NO":
                values.append("❌")
            elif col == "Channels":
                values.append(str(int(val)) if pd.notnull(val) else "")
            elif col == "Price":
                values.append(f"₹{int(val):,}")
            else:
                values.append(str(val))
        comparison_data[row["Model Name"]] = values

    st.dataframe(comparison_data.rename_axis("Feature").reset_index(), use_container_width=True)


# ---- Main App ----
def main():
    """
    Main function to run the Streamlit app.
    """
    st.set_page_config(page_title="Titan HA Selector", layout="wide")
    st.title("Titan HA Products")

    df = load_data()
    if df is None or df.empty:
        return

    filtered_df = render_sidebar_filters(df)
    if filtered_df.empty:
        st.warning("No products match your filters.")
        return

    filtered_df["Model Group"] = filtered_df["Model Name"].str.extract(r"^(\w+)", expand=False).str.upper()
    model_groups = sorted(filtered_df["Model Group"].dropna().unique())

    st.markdown("## Select Model Group")
    group_cols = st.columns(len(model_groups))
    for i, group in enumerate(model_groups):
        if group_cols[i].button(group):
            st.session_state.selected_group = group

    if "selected_group" not in st.session_state and model_groups:
        st.session_state.selected_group = model_groups[0]

    selected_group = st.session_state.get("selected_group")
    if not selected_group:
        return

    group_df = filtered_df[filtered_df["Model Group"] == selected_group]
    group_df = group_df.sort_values(by="Price", ascending=False)

    st.markdown(f"## All Models in {selected_group}")
    model_names = group_df["Model Name"].dropna().unique()
    st.markdown(f"🔍 **{len(model_names)} result(s) found**")

    for model_name in model_names:
        row = group_df[group_df["Model Name"] == model_name].iloc[0]
        show_model_card(row)
        st.markdown("---")

    # Show comparison in chunks of 4
    model_chunks = [model_names[i:i + 4] for i in range(0, len(model_names), 4)]
    for chunk in model_chunks:
        compare_df = group_df[group_df["Model Name"].isin(chunk)].drop_duplicates("Model Name")
        if len(compare_df) > 1:  # check the length
            show_comparison_table(compare_df)

if __name__ == "__main__":
    main()
