import streamlit as st
import pandas as pd
import os
from pathlib import Path

# If you have an external file pages.py, you can import from there.
# from app import pages

# Optional: If you have a title in pages.budget_page, you can reference it here.
# For demonstration, we'll just hardcode a title.
st.title("My Budget Page")

# Construct the correct file path
file_path = Path(os.getcwd()) / "data" / "budget.csv"

# List of known categories
expense_categories = [
    'Subscriptions & Recurring Expenses',
    'Planned Purchases',
    'Housing',
    'Utilities & Communications',
    'Groceries & Personal Items',
    'Transportation',
    'Insurance',
    'Debt Service',
    'Investing & Saving',
    'Discretionary Income'
]


# 1) LOAD DATA INTO SESSION STATE -------------------------------------------
def load_data():
    """
    Reads the CSV from disk and populates st.session_state with expense data.
    Each category in expense_categories is initialized as a list of dicts.
    """
    if "data_loaded" not in st.session_state:
        if file_path.exists():
            df = pd.read_csv(file_path)
        else:
            # If the file doesn't exist yet, create an empty DataFrame
            df = pd.DataFrame(columns=["Expense Category", "Expense Name", "Amount", "Frequency", "Notes"])

        # Initialize each category as an empty list in session state
        for cat in expense_categories:
            st.session_state[cat] = []

        # Populate each category list from the CSV
        for _, row in df.iterrows():
            cat = row.get("Expense Category", "")
            if cat in expense_categories:
                # Convert amount to float, stripping out "$" or commas if present
                amount_str = str(row.get("Amount", "0")).replace("$", "").replace(",", "")
                try:
                    amount_val = float(amount_str)
                except:
                    amount_val = 0.0

                # Frequency and Notes
                freq = row.get("Frequency", "Monthly")
                notes = row.get("Notes", "")

                # Build the expense dict
                expense_dict = {
                    "name": row.get("Expense Name", ""),
                    "cost": amount_val,
                    "frequency": freq,
                    "notes": notes
                }

                # Add it to the corresponding list in session state
                st.session_state[cat].append(expense_dict)

        # Mark that data has been loaded so we don’t reload on every run
        st.session_state["data_loaded"] = True


# 2) SAVE DATA BACK TO CSV -------------------------------------------------
def save_data():
    """
    Gathers all expenses from session state and writes them to the CSV file.
    """
    data_rows = []
    for cat in expense_categories:
        for exp in st.session_state[cat]:
            data_rows.append({
                "Expense Category": cat,
                "Expense Name": exp["name"],
                "Amount": exp["cost"],
                "Frequency": exp["frequency"],
                "Notes": exp["notes"]
            })

    # Convert to DataFrame and save
    df = pd.DataFrame(data_rows)
    df.to_csv(file_path, index=False)
    st.success("Budget saved successfully!")


# 3) INITIALIZE/HELPER FUNCTIONS -------------------------------------------
def init_category(category_name):
    """Ensure a list exists for this category in session state."""
    if category_name not in st.session_state:
        st.session_state[category_name] = []


def add_expense(category_name):
    """Append a new expense with default values."""
    init_category(category_name)
    st.session_state[category_name].append({
        "name": "",
        "cost": 0.0,
        "frequency": "Monthly",
        "notes": ""
    })


def delete_expense(category_name, index):
    """Delete an expense from a given category at the specified index."""
    init_category(category_name)
    if 0 <= index < len(st.session_state[category_name]):
        st.session_state[category_name].pop(index)


def render_expense_category(category_name):
    """
    Renders an expander for the given category name,
    showing all expenses in session state with edit/delete capabilities.
    """
    init_category(category_name)

    with st.expander(label=category_name, expanded=True):
        st.subheader(category_name)

        # Display each expense row dynamically
        for idx, expense in enumerate(st.session_state[category_name]):
            cols = st.columns([1, 1, 1, 1, 0.25])
            with cols[0]:
                expense["name"] = st.text_input(
                    label="Expense Name",
                    value=expense["name"],
                    key=f"{category_name}_name_{idx}"
                )
            with cols[1]:
                expense["cost"] = st.number_input(
                    label="Cost ($)",
                    value=expense["cost"],
                    key=f"{category_name}_cost_{idx}"
                )
            with cols[2]:
                options = ['Weekly', 'Semi-Monthly', 'Monthly', 'Semester', 'Quarterly', 'Annually']
                # Default to "Monthly" if current frequency is not in the list
                default_index = options.index(expense["frequency"]) if expense["frequency"] in options else 2
                expense["frequency"] = st.selectbox(
                    label="Frequency",
                    options=options,
                    index=default_index,
                    key=f"{category_name}_frequency_{idx}"
                )
            with cols[3]:
                expense["notes"] = st.text_input(
                    label="Notes",
                    value=expense["notes"],
                    key=f"{category_name}_notes_{idx}"
                )
            with cols[4]:
                st.markdown("<br>", unsafe_allow_html=True)
                if st.button("❌", key=f"{category_name}_delete_{idx}"):
                    delete_expense(category_name, idx)
                    st.rerun()

        # Button to add a new expense within this category
        if st.button("Add Expense", key=f"{category_name}_add"):
            add_expense(category_name)
            st.rerun()


# 4) MAIN APP LOGIC --------------------------------------------------------
load_data()  # Make sure we load data into session state first.

lhs_col, rhs_col = st.columns([3, 1])

with lhs_col:
    # Render each known category
    for expense_category in expense_categories:
        render_expense_category(expense_category)

with rhs_col:
    # Button to save all changes back to CSV
    if st.button(label="Save Budget", use_container_width=True, type="primary"):
        save_data()

    # Optionally, a placeholder for "Open Budget" or "Add Expense Category"
    st.button(label="Open Budget", use_container_width=True, type="primary")
    st.button(label="Add Expense Category", use_container_width=True, type="primary")

# (Optional) Display data in a table for reference
# This will show you what's currently in session state or on disk if you reload
st.write("### Current Budget Data")
all_data = []
for cat in expense_categories:
    for exp in st.session_state[cat]:
        all_data.append({
            "Expense Category": cat,
            "Expense Name": exp["name"],
            "Amount": exp["cost"],
            "Frequency": exp["frequency"],
            "Notes": exp["notes"]
        })
st.dataframe(pd.DataFrame(all_data))
