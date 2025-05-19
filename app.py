import streamlit as st
import pandas as pd

# ---- Load data ----
@st.cache_data

def load_data():
    try:
        df = pd.read_excel("sourcedata.xlsx")
        df.columns = df.columns.str.strip()

        if "Augmented Focus.1" in df.columns and "Augmented Focus" in df.columns:
            df["Augmented Focus"] = df["Augmented Focus"].combine_first(df["Augmented Focus.1"])
            df.drop(columns=["Augmented Focus.1"], inplace=True)

        df["Price"] = pd.to_numeric(
            df["Price"].astype(str).str.replace(",", ""), errors="coerce"
        ).fillna(0).astype(int)

        for col in df.select_dtypes(include="object").columns:
            df[col] = df[col].astype(str).str.strip().str.upper()

        return df
    except FileNotFoundError:
        st.error("❌ Error: 'sourcedata.xlsx' not found.")
        return None

# ---- Sidebar Filters ----
def render_sidebar_filters(df):
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
            elif price_bucket == "3,00,000+":
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

# ---- Comparison Table ----
def render_comparison_sets(group_df):
    st.subheader("Comparison Table")
    models_sorted = group_df.sort_values(by="Price", ascending=False)
    model_names = sorted(models_sorted["Model Name"].dropna().unique(), key=lambda x: models_sorted[models_sorted['Model Name'] == x]['Price'].iloc[0], reverse=True)

    chunks = [model_names[i:i + 4] for i in range(0, len(model_names), 4)]

    for models in chunks:
        subset_df = group_df[group_df["Model Name"].isin(models)]
        feature_cols = [col for col in subset_df.columns if col not in ["Model Name", "Price", "Quantity", "Degree of loss", "Channels", "Model Group"]]

        header = ["Feature"] + models
        table = []

        for feature in feature_cols:
            row = [feature]
            for model in models:
                val = subset_df[subset_df["Model Name"] == model][feature].iloc[0].upper()
                if val == "YES":
                    row.append("✅")
                elif val == "NO":
                    row.append("❌")
                else:
                    row.append(val)
            table.append(row)

        st.table(pd.DataFrame(table, columns=header))

# ---- Main App ----
def main():
    st.set_page_config(page_title="Titan HA Selector", layout="wide")
    st.title("Titan HA Products")

    df = load_data()
    if df is None or df.empty:
        return

    filtered_df = render_sidebar_filters(df)
    if filtered_df.empty:
        st.warning("No products match your filters.")
        return

    filtered_df["Model Group"] = filtered_df["Model Name"].str.extract(r"^([A-Z]+)", expand=False).str.upper()
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
    models_sorted = group_df.sort_values(by="Price", ascending=False)
    model_names = sorted(models_sorted["Model Name"].dropna().unique(), key=lambda x: models_sorted[models_sorted['Model Name'] == x]['Price'].iloc[0], reverse=True)

    st.markdown(f"### All Models in {selected_group}")

    for model in model_names:
        model_row = group_df[group_df["Model Name"] == model].iloc[0]

        st.markdown(f"#### 🧩 {model}")
        with st.container():
            image_url = "https://cdn.signia.net/-/media/signia/global/images/products/other-hearing-aids/orion-chargego/orion-charge-go_ric_black_1000x1000.jpg?rev=c993db8a8cb6470692b613a45f701c47&extension=webp&hash=5F307282D586208C92013BA20A652A59"
            if selected_group.upper() == "ORION":
                st.image(image_url, width=150)

            st.markdown(
                f"""
                <div style="border:1px solid #ccc; padding:15px; border-radius:10px; background-color:#f9f9f9;">
                    <p><strong>Channels:</strong> {model_row['Channels']}</p>
                    <p><strong>Price:</strong> ₹{model_row['Price']}</p>
                </div>
                """,
                unsafe_allow_html=True
            )

            other_features = [
                col for col in group_df.columns
                if col not in ["Model Name", "Price", "Quantity", "Degree of loss", "Channels", "Model Group"]
            ]

            for col in other_features:
                val = str(model_row[col]).upper()
                if val == "YES":
                    st.markdown(f"✅ {col}")
                elif val == "NO":
                    st.markdown(f"❌ {col}")
                else:
                    st.markdown(f"🔹 **{col}:** {model_row[col]}")

            st.markdown("---")

    render_comparison_sets(group_df)

if __name__ == "__main__":
    main()
