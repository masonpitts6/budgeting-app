import streamlit as st
import pandas as pd
import os
from pathlib import Path
import app.config as config
import plotly.express as px

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
                freq = row.get("Frequency", config.FREQUENCIES[1])
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

        cost_ls = []
        expense_ls = []
        for idx, expense in enumerate(st.session_state[category_name]):
            cost_ls = cost_ls + [expense['cost']]
            expense_ls = expense_ls + [expense['name']]

        cols = st.columns(4)

        with cols[0]:
            st.metric(
                label='Weekly Cost',
                value=f'${sum(cost_ls):,.0f}'
            )

        with cols[1]:
            st.metric(
                label='Monthly Cost',
                value=f'${sum(cost_ls):,.0f}'
            )

        with cols[2]:
            st.metric(
                label='Annual Cost',
                value=f'${sum(cost_ls):,.0f}'
            )

        with cols[3]:
            st.metric(
                label='Percentage of Income',
                value=f'25%'
            )

        st.markdown('<br>', unsafe_allow_html=True)

        cols = st.columns(2)

        with cols[0]:

            cost_data = pd.DataFrame({
                "Cost Type": ["Weekly", "Monthly", "Quarterly", "Annual"],
                "Amount": [sum(cost_ls)] * 4
            })

            st.subheader("📊 Cost Breakdown Chart")
            st.markdown('<br><br>', unsafe_allow_html=True)
            st.bar_chart(cost_data.set_index("Cost Type"))

        with cols[1]:

            pie_data = pd.DataFrame(
                {
                    'Category': expense_ls,
                    'Amount': cost_ls
                }
            )
            st.subheader('Category Breakdown')
            fig3 = px.pie(pie_data, names="Category", values="Amount")
            fig3.update_layout(height=400, width=400, legend=dict(
                orientation="h",  # Horizontal legend
                yanchor="top",  # Align from the top
                y=-0.3,  # Adjust this value downward if overlapping occurs (e.g., -0.4)
                xanchor="center",
                x=0.5
            ),
                               margin=dict(t=50, b=100))
            st.plotly_chart(fig3, use_container_width=True)

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
                # Default to "Monthly" if current frequency is not in the list
                default_index = config.FREQUENCIES.index(expense["frequency"]) \
                    if expense["frequency"] in config.FREQUENCIES else 2

                expense["frequency"] = st.selectbox(
                    label="Frequency",
                    options=config.FREQUENCIES,
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
    with st.expander(label='💰 Budget Overview', expanded=True):
        data = {
            "Expense": [
                "Subscriptions & Recurring Expenses", "Planned Purchases", "Rent", "Electricity", "Water", "Internet",
                "Phone bill", "Groceries", "Gas", "Health Insurance", "Dental Insurance", "Vision Insurance",
                "Renter's Insurance", "Car Insurance", "Life Insurance", "Short-term Disability",
                "Long-term Disability",
                "Car Payment", "Retirement Investing", "Personal Investing", "Savings", "Student Loan Payments",
                "Discretionary Income", "Car Maintenance", "Dog Day Care", "Pet Insurance", "Critical Illness",
                "Critical Accident", "Legal Services", "Health Savings Account"
            ],
            "Expense Category": [
                "Subscriptions & Recurring Expenses", "Planned Purchases", "Housing", "Utilities & Communications",
                "Utilities & Communications", "Utilities & Communications", "Utilities & Communications",
                "Food & Personal Items", "Gas & Transportation", "Insurance", "Insurance", "Insurance", "Insurance",
                "Insurance", "Insurance", "Insurance", "Insurance", "Gas & Transportation", "Investing & Savings",
                "Investing & Savings", "Investing & Savings", "Debt Service", "Discretionary Income",
                "Gas & Transportation", "Discretionary Income", "Insurance", "Insurance", "Insurance", "Insurance",
                "Investing & Savings"
            ],
            "Weekly": [
                164.65, 192.31, 524.54, 46.15, 23.08, 11.54, 40.53, 200.00, 100.00, 87.11, 12.48, 2.26, 6.75,
                153.92, 1.04, 0.00, 1.35, 193.38, 57.69, 0.00, 0.00, 203.65, 400.00, 57.69, 80.00, 11.54, 4.02,
                3.43, 3.76, 51.28
            ],
            "Monthly": [
                713.48, 833.33, 2273.00, 200.00, 100.00, 50.00, 175.64, 866.67, 433.33, 377.47, 54.09, 9.80, 29.25,
                667.00, 4.50, 0.00, 5.86, 838.00, 250.00, 0.00, 0.00, 882.50, 1733.33, 250.00, 346.67, 50.00, 17.44,
                14.86, 16.30, 222.22
            ],
            "Annual": [
                8561.76, 10000.00, 27276.00, 2400.00, 1200.00, 600.00, 2107.68, 10400.00, 5200.00, 4529.66, 649.09,
                117.57, 351.00, 8004.00, 54.00, 0.00, 70.32, 10056.00, 3000.00, 0.00, 0.00, 10590.00, 20800.00,
                3000.00, 4160.00, 600.00, 209.28, 178.32, 195.60, 2666.64
            ],
            "Percentage of Income": [
                "4.9%", "5.7%", "15.6%", "1.4%", "0.7%", "0.3%", "1.2%", "5.9%", "3.0%", "2.6%", "0.4%", "0.1%",
                "0.2%", "4.6%", "0.0%", "0.0%", "0.0%", "5.7%", "1.7%", "0.0%", "0.0%", "6.0%", "11.9%", "1.7%",
                "2.4%", "0.3%", "0.1%", "0.1%", "0.1%", "1.5%"
            ]
        }

        # Convert to DataFrame
        df = pd.DataFrame(data)

        # Format currency values with "$" symbol
        df["Weekly"] = df["Weekly"].apply(lambda x: f"${x:,.2f}")
        df["Monthly"] = df["Monthly"].apply(lambda x: f"${x:,.2f}")
        df["Annual"] = df["Annual"].apply(lambda x: f"${x:,.2f}")

        # Streamlit App Title
        st.title("💰 Budget Overview")

        cols = st.columns(2)
        with cols[0]:
            st.title('Bar Chart Here')

        with cols[1]:
            st.title('Pie Chart Here')

        tabs = st.tabs(["📊 Budget Table", ] + expense_categories)

        with tabs[0]:
            # Define custom CSS for correct table rendering in Streamlit
            table_style = """
                <style>
                    .styled-table {
                        width: 100%;
                        border-collapse: collapse;
                        font-family: Arial, sans-serif;
                        font-size: 14px;
                        margin-top: 20px;
                    }
                    .styled-table th {
                        background-color: #004466;
                        color: white;
                        text-align: center;
                        padding: 12px;
                        font-size: 16px;
                    }
                    .styled-table td {
                        padding: 10px;
                        border-bottom: 1px solid #ddd;
                        text-align: right;
                    }
                    .styled-table tr:nth-child(even) {
                        background-color: #f2f2f2;
                    }
                    .styled-table tr:hover {
                        background-color: #d9ebf9;
                    }
                    .styled-table td:first-child, .styled-table td:nth-child(2) {
                        text-align: left;
                        font-weight: bold;
                    }
                    .highlight {
                        background-color: #ffcccc !important;
                        font-weight: bold;
                        padding: 5px;
                    }
                </style>
            """

            # Highlight high annual expenses (> $5,000)
            df["Annual"] = df["Annual"].apply(
                lambda x: f'<span class="highlight">{x}</span>' if float(
                    x.replace("$", "").replace(",", "")) > 5000 else x)

            # Convert DataFrame to HTML
            table_html = df.to_html(index=False, escape=False, classes="styled-table")

            # ✅ Correct Way to Render the Table in Streamlit
            st.write(table_style, unsafe_allow_html=True)  # Load CSS first
            st.write(table_html, unsafe_allow_html=True)  # Render the table separately

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
