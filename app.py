import streamlit as st
import pandas as pd
import numpy as np
from PIL import Image

# Load and preprocess data
def load_data():
    df = pd.read_csv("ha_data.csv")
    df.fillna("", inplace=True)
    return df

def format_price(price):
    return f"INR {price:,.0f}" if price else "-"

# Load Data
df = load_data()
model_groups = df['Group'].dropna().unique().tolist()

# UI
st.title("Titan HA Products")

# ---- Group Selection with Image Preview ----
st.markdown("## Select Model Group")

group_cols = st.columns(len(model_groups))
for i, group in enumerate(model_groups):
    if group_cols[i].button(group):
        st.session_state.selected_group = group

# Set default group if not already selected
if "selected_group" not in st.session_state and model_groups:
    st.session_state.selected_group = model_groups[0]

selected_group = st.session_state.get("selected_group")
if not selected_group:
    st.stop()

# Optional: Display image for specific group
if selected_group == "ORION":
    st.image(
        "https://cdn.signia.net/-/media/signia/global/images/products/other-hearing-aids/orion-chargego/orion-charge-go_ric_black_1000x1000.jpg?rev=c993db8a8cb6470692b613a45f701c47&extension=webp&hash=5F307282D586208C92013BA20A652A59",
        caption="ORION Model Preview",
        use_column_width=True
    )

# Filter data by selected group
filtered_df = df[df['Group'] == selected_group]
filtered_df = filtered_df.sort_values(by='Price', ascending=False)

# Extract feature columns (all except Model, Group, Price)
feature_cols = [col for col in df.columns if col not in ['Model', 'Group', 'Price']]

# Display model cards
st.subheader("Available Models")
for _, row in filtered_df.iterrows():
    with st.container():
        st.markdown(f"### {row['Model']}")
        col1, col2 = st.columns([1, 3])
        with col1:
            st.markdown(f"**Price:** {format_price(row['Price'])}")
        with col2:
            st.markdown("**Features:**")
            for feat in feature_cols:
                if str(row[feat]).strip().lower() == 'yes':
                    st.markdown(f"- ✅ {feat}")
                elif str(row[feat]).strip().lower() == 'no':
                    st.markdown(f"- ❌ {feat}")

# Display comparison table at the bottom
st.subheader("Model Comparison")

# Split models into groups of 4 for comparison
max_compare = 4
comparison_chunks = [filtered_df.iloc[i:i + max_compare] for i in range(0, len(filtered_df), max_compare)]

for chunk in comparison_chunks:
    model_names = chunk['Model'].tolist()
    comparison_data = {'Feature': feature_cols}

    for _, row in chunk.iterrows():
        comparison_data[row['Model']] = [
            '✅' if str(row[feat]).strip().lower() == 'yes' else
            '❌' if str(row[feat]).strip().lower() == 'no' else
            '-' for feat in feature_cols
        ]

    comp_df = pd.DataFrame(comparison_data)
    st.table(comp_df.set_index('Feature'))
