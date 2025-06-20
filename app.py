import streamlit as st
import pandas as pd
import os
import re

# ---- Load Data ----
@st.cache_data
def load_data():
    try:
        df = pd.read_excel("sourcedata.xlsx")
        df.columns = df.columns.str.strip()

        if "Augmented Focus.1" in df.columns and "Augmented Focus" in df.columns:
            df["Augmented Focus"] = df["Augmented Focus"].combine_first(df["Augmented Focus.1"])
            df.drop(columns=["Augmented Focus.1"], inplace=True)

        df["Price"] = pd.to_numeric(df["Price"].astype(str).str.replace(",", ""), errors="coerce").fillna(0).astype(int)

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
                options=["30,000 – 1,00,000", "1,00,000 – 300,000", "300,000+"]
            )
            if price_bucket == "30,000 – 1,00,000":
                filtered_df = filtered_df[(filtered_df[col] >= 30000) & (filtered_df[col] < 100000)]
            elif price_bucket == "1,00,000 – 300,000":
                filtered_df = filtered_df[(filtered_df[col] >= 100000) & (filtered_df[col] < 300000)]
            elif price_bucket == "300,000+":
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
    if models_df.shape[0] < 2:
        return

    st.markdown("## 📊 Feature Comparison")

    feature_descriptions = {
        "Channels": "The number of frequency channels for sound processing.",
        "Price": "Cost of the model in Indian Rupees (₹).",
        "Android and iOS Streaming": "Direct audio streaming from both Android and Apple devices for calls, music, and more.",
        "Bluetooth": "Wireless connectivity for direct streaming and connection to the Signia app.",
        "Augmented Focus": "Two processors separate speech for clarity and surrounding sounds for a natural experience in noise.",
        "Echo Shield": "Reduces echoes and reverberation in challenging acoustic environments for clearer sound.",
        "Tinnitus Manager": "Offers various sound therapy options, including Notch Therapy, to help manage tinnitus.",
        "HD Music": "Enhances the sound quality for non-streamed music listening.",
        "Noise Management": "Advanced technology to reduce background noise and improve speech clarity."
    }

    comparison_cols = ["Channels", "Price"]
    other_cols = [col for col in models_df.columns if col not in ["Model Name", "Quantity", "Degree of loss", "Model Group"] + comparison_cols]
    comparison_cols += other_cols

    comparison_data = pd.DataFrame(index=comparison_cols)

    for _, row in models_df.iterrows():
        values = []
        for col in comparison_cols:
            val = row.get(col, "")
            if str(val).upper() == "YES":
                values.append("✅")
            elif str(val).upper() == "NO":
                values.append("❌")
            elif col == "Channels":
                values.append(str(int(val)) if pd.notnull(val) and str(val).isdigit() else str(val))
            elif col == "Price":
                values.append(f"₹{int(val):,}")
            else:
                values.append(str(val))
        comparison_data[row["Model Name"]] = values

    descriptions = [feature_descriptions.get(feature, "") for feature in comparison_data.index]
    comparison_data.insert(0, "Description", descriptions)

    st.dataframe(comparison_data.rename_axis("Feature").reset_index(), use_container_width=True)

# ---- Function to extract model number for sorting ----
def get_model_number(model_name):
    match = re.search(r'(\d+)(IX|AX|X)', model_name)
    if match:
        return int(match.group(1)), match.group(2)
    return 0, ''

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

    filtered_df["Model Group"] = filtered_df["Model Name"].fillna("").str.extract(r"^(\w+)", expand=False).str.upper()

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

    if len(model_groups) == 1:
        st.session_state.selected_group = model_groups[0]
    elif "selected_group" not in st.session_state or st.session_state.selected_group not in model_groups:
        st.session_state.selected_group = model_groups[0]

    selected_group = st.session_state.get("selected_group")
    if not selected_group:
        return

    if selected_group not in model_groups:
        st.session_state.selected_group = model_groups[0]
        selected_group = st.session_state.selected_group

    # ---- Show image for selected group ----
    group_images = {
        "ORION": ("https://cdn.signia.net/-/media/signia/global/images/products/other-hearing-aids/orion-chargego/orion-charge-go_ric_black_1000x1000.jpg", "Orion Charge&Go RIC"),
        "PURE": ("https://cdn.signia.net/-/media/signia/global/images/products/signia-ax/pure-chargego-ax/pure-charge-go-ax_graphite_standard-charger_1920x1080.jpg", "Pure Charge&Go AX"),
        "SILK": ("https://cdn.signia.net/-/media/signia/global/images/campaigns/signia-ix/silk-chargego-ix/signia-ix_silk-chgo_hearing-aids-out-of-charger_circle_400x400.png", "Silk Charge&Go IX"),
        "STYLETTO": ("https://cdn.signia.net/-/media/signia/global/images/campaigns/signia-ix/styletto-ix/styletto-ix_taking-out-of-charger_circle_1000x1000.jpg?w=1900&rev=475793246f23409381e3246ffa4ae02b&extension=webp&hash=610D7361287B6F35A17FD339D07421B2", "Styletto IX"),
        "MOTION": ("https://cdn.signia.net/-/media/signia/global/images/products/xperience/motion-sp-x/motion_cng_sp_x_pair_dark_champagne_1920x1080.jpg?w=1900&rev=822053d628c74adeb332a181feba1226&extension=webp&hash=A80732C51303ECE212DAA0F8A544E9C1", "Motion Charge&Go SP X"),
        "INTUIS": ("https://cdn.signia.net/-/media/signia/global/images/products/other-hearing-aids/intuis-4/intuis-s-4_graphite.png?rev=36cb4ea1efc442a5810a1290448e2828&extension=webp&hash=0A71216A7C97C44BD42A63092DC75345", "Intuis S 4")
    }

    if selected_group in group_images:
        st.image(group_images[selected_group][0], caption=group_images[selected_group][1], width=300)

    group_df = filtered_df[filtered_df["Model Group"] == selected_group].copy()
    if not group_df.empty:
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
