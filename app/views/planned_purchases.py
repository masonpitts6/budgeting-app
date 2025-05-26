import streamlit as st
import pandas as pd
import os
from pathlib import Path
from app import pages

st.title(pages.planned_purchases.title)

file_path = Path(os.getcwd()) / "data" / "planned_purchases.csv"

# Read the CSV file
planned_purchases_data = pd.read_csv(file_path)

tabs = st.tabs(['Summary', 'Statistics', 'Planned Purchases', 'Settings'])

with tabs[0]:
    # Display the dataframe in Streamlit
    height = 625 if planned_purchases_data.shape[0] > 10 else None

    st.dataframe(
        planned_purchases_data,
        height=height,
        use_container_width=True,
        hide_index=True
    )