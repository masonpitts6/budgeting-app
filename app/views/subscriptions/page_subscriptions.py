import streamlit as st
import pandas as pd
import os
from pathlib import Path
from app import pages
from app.views.subscriptions.tabs import subscriptions

st.title(pages.subscriptions_page.title)

# Construct the correct file path
file_path = Path(os.getcwd()) / "data" / "subscriptions.csv"

# Read the CSV file
subscription_data = pd.read_csv(file_path)

tabs = st.tabs(
    [
        'Summary',
        'Statistics',
        'Subscriptions',
        'Settings'
    ]
)

with tabs[0]:
    # Display the dataframe in Streamlit
    height = 625 if subscription_data.shape[0] > 10 else None

    # Display the dataframe in Streamlit
    st.dataframe(
        data=subscription_data,
        height=height,
        use_container_width=True,
        hide_index=True
    )


with tabs[2]:
    subscriptions.render_subscriptions_tab(
        subscription_data=subscription_data,
    )