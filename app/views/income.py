import streamlit as st
import pandas as pd
import os
from pathlib import Path
from app import pages

st.title(pages.income_page.title)

# Construct the correct file path
file_path = Path(os.getcwd()) / "data" / "income.csv"

# Read the CSV file
income_data = pd.read_csv(file_path)

lhs_col, rhs_col = st.columns(2)

with rhs_col:
    # Initialize session state for income sources
    if "income_sources" not in st.session_state:
        st.session_state.income_sources = [1]  # Start with Income 1

    if "income_values" not in st.session_state:
        st.session_state.income_values = {}

    # Convert DataFrame column to a list for selectbox options
    job_titles = income_data["Job Title"].tolist()


    # Function to add a new income source dynamically
    def add_income_source():
        if st.session_state.income_sources:
            new_income_id = max(st.session_state.income_sources) + 1  # Get the next available number
        else:
            new_income_id = 1  # Default to 1 if all were removed
        st.session_state.income_sources.append(new_income_id)


    # Function to remove an income source
    def remove_income_source(source_id):
        if len(st.session_state.income_sources) > 1:
            # Remove selected income source while preserving order
            st.session_state.income_sources = [inc for inc in st.session_state.income_sources if inc != source_id]
            # Remove stored selection values
            selection_keys = [key for key in st.session_state.income_values if key == f"income_{source_id}"]
            for key in selection_keys:
                del st.session_state.income_values[key]


    # Function to reset income sources
    def reset_income_sources():
        st.session_state.income_sources = [1]  # Reset to only Income 1
        st.session_state.income_values = {"income_1": job_titles[0]}  # Reset to default value


    # Display select boxes with remove buttons
    for income_id in sorted(st.session_state.income_sources):  # Ensure proper ordering
        cols = st.columns([4, 1])  # Adjust column width: 4x for selectbox, 1x for button

        with cols[0]:  # Selectbox column
            default_value = st.session_state.income_values.get(f"income_{income_id}", job_titles[0])
            selected_value = st.selectbox(
                label=f"Income {income_id}",
                options=job_titles,
                index=job_titles.index(default_value) if default_value in job_titles else 0,
                key=f"income_{income_id}"
            )
            st.session_state.income_values[f"income_{income_id}"] = selected_value  # Store selection persistently

        with cols[1]:  # Remove button column
            st.markdown("<br>", unsafe_allow_html=True)  # Adds spacing
            st.button("❌", key=f"remove_{income_id}", on_click=remove_income_source, args=(income_id,), use_container_width=True)

    # Create columns for buttons to align them in the same row
    button_cols = st.columns([1, 1])  # Two equal-sized columns

    with button_cols[0]:
        st.button("➕ Add New Income Source", on_click=add_income_source, use_container_width=True)

    with button_cols[1]:
        st.button("🔄 Reset", on_click=reset_income_sources, use_container_width=True)

with lhs_col:

    for income in st.session_state.income_values.values():
        st.markdown(
            f"""
            <div style="border:2px solid #ddd; padding: 15px; border-radius: 10px; margin-bottom: 15px; background-color: #f9f9f9;">
                <h3 style="text-align: center;">{income}</h3>
            </div>
            """,
            unsafe_allow_html=True
        )

        income_df = income_data[income_data['Job Title'] == income]

        # Create columns for Salary, Bonus, and Total Compensation
        cols = st.columns(3)

        with cols[0]:
            st.metric(label="Salary", value=f"${income_df['Salary'].item()}")

        with cols[1]:
            st.metric(label="Bonus", value=f"${income_df['Bonus'].item()}")

        with cols[2]:
            st.metric(label="Total Compensation", value=f"${income_df['Total Compensation'].item()}")




# Display the dataframe in Streamlit
st.dataframe(income_data)
