import streamlit as st
import pandas as pd
import os
from pathlib import Path
from app import pages

st.title(pages.budget_page.title)

# Construct the correct file path
file_path = Path(os.getcwd()) / "data" / "budget.csv"

# Read the CSV file
income_data = pd.read_csv(file_path)

# Display the dataframe in Streamlit
st.dataframe(income_data)
