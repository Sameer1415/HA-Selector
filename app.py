import streamlit as st
import pandas as pd
import os

# Load and preprocess data
def load_data():
    uploaded_file = st.sidebar.file_uploader("Upload Titan Product CSV", type=["csv"])
    if uploaded_file:
        df = pd.read_csv(uploaded_file)
        df.dropna(subset=["Model Name"], inplace=True)
        return df
    return None

# Sidebar filters
def render_sidebar_filters(df):
    st.sidebar.header("Filter Options")
    filtered_df = df.copy()

    product_types = st.sidebar.multiselect("Select Product Type", df["Product Type"].dropna().unique())
    if product_types:
        filtered_df = filtered_df[filtered_df["Product Type"].isin(product_types)]

    price_range = st.sidebar.slider("Price Range", 0, int(df["MRP"].max()), (0, int(df["MRP"].max())))
    filtered_df = filtered_df[(filtered_df["MRP"] >= price_range[0]) & (filtered_df["MRP"] <= price_range[1])]

    return filtered_df

# Extract model number and suffix
def get_model_number(name):
    import re
    match = re.search(r"(\d+)([A-Z]*)", name.upper())
    if match:
        return int(match.group(1)), match.group(2)
    return 0, ""

# Display model card
def show_model_card(row):
    st.subheader(row["Model Name"])
    st.write(f"**Product Type:** {row['Product Type']}")
    st.write(f"**MRP:** ₹{row['MRP']:,}")
    st.write(f"**Battery:** {row['Battery']}" if 'Battery' in row else "")
    st.write(f"**Fitting Range:** {row['Fitting Range']}" if 'Fitting Range' in row else "")
    st.write(f"**Technology Level:** {row['Technology Level']}" if 'Technology Level' in row else "")
    if 'Key Features' in row and pd.notna(row['Key Features']):
        st.markdown(f"**Key Features:** {row['Key Features']}")

# Comparison table
def show_comparison_table(df):
    st.dataframe(df.set_index("Model Name"))

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

    filtered_df["Model Group"] = filtered_df["Model Name"].str.extract(r"^(\w+)", expand=False).str.upper()

    group_order = ["IX", "AX", "X", "ORION"]
    filtered_df["Group Rank"] = filtered_df["Model Group"].apply(lambda x: group_order.index(x) if x in group_order else len(group_order))

    filtered_df['Model Number'], filtered_df['Model Suffix'] = zip(*filtered_df['Model Name'].map(get_model_number))
    filtered_df.sort_values(by=["Group Rank", "Model Suffix", "Model Number"], ascending=[True, False, False], inplace=True)

    model_groups = filtered_df["Model Group"].dropna().unique()

    st.markdown("## Select Model Group")
    group_cols = st.columns(len(model_groups))
    for i, group in enumerate(model_groups):
        if group_cols[i].button(group):
            st.session_state.selected_group = group

    if "selected_group" not in st.session_state and len(model_groups):
        st.session_state.selected_group = model_groups[0]

    selected_group = st.session_state.get("selected_group")
    if not selected_group:
        return

    # Show image for selected group
    group_images = {
        "ORION": "https://cdn.signia.net/-/media/signia/global/images/products/other-hearing-aids/orion-chargego/orion-charge-go_ric_black_1000x1000.jpg?rev=c993db8a8cb6470692b613a45f701c47&extension=webp&hash=5F307282D586208C92013BA20A652A59",
        "PURE": "https://cdn.signia.net/-/media/signia/global/images/products/signia-ax/pure-chargego-ax/pure-charge-go-ax_graphite_standard-charger_1920x1080.jpg?w=1900&rev=4267d686857b4e5ea44e31f288945288&extension=webp&hash=75060B7C704F1EA9AC83983E9E37B5B5",
        "SILK": "https://cdn.signia.net/-/media/signia/global/images/campaigns/signia-ix/silk-chargego-ix/signia-ix_silk-chgo_hearing-aids-out-of-charger_circle_400x400.png?w=1900&rev=3711106411534e0a95bc417926f4baff&extension=webp&hash=0C6D82637204A9A70859375B12A2A464"
    }

    image_url = group_images.get(selected_group)
    if image_url:
        st.image(image_url, caption=f"{selected_group.title()} Image", use_column_width=True)
    else:
        image_path = f"images/{selected_group}.png"
        if os.path.exists(image_path):
            st.image(image_path, use_column_width=True)

    group_df = filtered_df[filtered_df["Model Group"] == selected_group].copy()
    group_df['Model Number'], group_df['Model Suffix'] = zip(*group_df['Model Name'].map(get_model_number))
    group_df.sort_values(by=["Model Suffix", "Model Number"], ascending=[False, False], inplace=True)

    st.markdown(f"## All Models in {selected_group}")
    model_names = group_df["Model Name"].dropna().unique()
    st.markdown(f"🔍 **{len(model_names)} result(s) found**")

    for model_name in model_names:
        row = group_df.drop(columns=['Group Rank', 'Model Number', 'Model Suffix'], errors='ignore')[group_df["Model Name"] == model_name].iloc[0]
        show_model_card(row)
        st.markdown("---")

    if len(model_names) > 1:
        st.markdown(f"## 🔄 Comparison Table for {selected_group}")
        show_comparison_table(group_df.drop_duplicates("Model Name").drop(columns=['Group Rank', 'Model Number', 'Model Suffix'], errors='ignore'))

if __name__ == "__main__":
    main()
