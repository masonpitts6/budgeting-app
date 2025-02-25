import streamlit as st
import pandas as pd
import os
from pathlib import Path
from app import pages

st.title(pages.planned_purchases.title)

file_path = Path(os.getcwd()) / "data" / "planned_purchases.csv"

# Read the CSV file
planned_purchases_data = pd.read_csv(file_path)

# Display the dataframe in Streamlit
st.dataframe(planned_purchases_data)