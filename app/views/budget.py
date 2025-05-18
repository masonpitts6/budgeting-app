import datetime
import math
from typing import List

import pandas as pd
import streamlit as st
from streamlit.delta_generator import DeltaGenerator


def compute_step(amount: float) -> int:
    """
    Compute a step size that’s the nearest power of ten for the given amount.
    E.g. 7.25 → 1, 42.50 → 10, 327 → 100, 2300 → 1000.

    Args:
        amount (float): The expense amount.

    Returns:
        int: 10**floor(log10(amount)) or 1 if amount ≤ 0.
    """
    if amount <= 0:
        return 1
    exponent = math.floor(math.log10(amount))
    return 10 ** max(exponent - 1, 0)


def save_expense(
        expense_id: int,
        name: str,
        amount: float,
        frequency: str,
        last_updated: datetime.date,
        notes: str,
) -> None:
    """
    Handle saving an edited expense entry.

    Args:
        expense_id (int): ID of the expense to edit.
        name (str): Updated name.
        amount (float): Updated amount.
        frequency (str): Updated frequency.
        last_updated (datetime.date): Updated date.
        notes (str): Updated notes.
    """
    # TODO: implement your actual save logic
    st.success(
        f'Expense {expense_id} saved:\n'
        f'• Name: {name}\n'
        f'• Amount: ${amount:,.2f}\n'
        f'• Frequency: {frequency}\n'
        f'• Last Updated: {last_updated}\n'
        f'• Notes: {notes or "(none)"}'
    )


def delete_expense(expense_id: int) -> None:
    """
    Handle deleting an expense entry.

    Args:
        expense_id (int): ID of the expense to delete.
    """
    # TODO: implement your actual delete logic
    st.warning(f'Deleted expense with ID {expense_id}')


def render_expenses_tab(
        expense_tab: DeltaGenerator,
        budget_data: pd.DataFrame,
        expense_categories: List[str],
        frequency_options: List[str],
) -> None:
    """
    Render the Expenses tab, grouping each row in its own st.form.

    Args:
        expense_tab (DeltaGenerator): The Streamlit tab/container to render into.
        budget_data (pd.DataFrame): DataFrame of budget items with columns:
            ['ID','Date','Category','Name','Amount','Frequency','Notes','Status','Category Emoji'].
        expense_categories (List[str]): Ordered list of unique categories to display.
        frequency_options (List[str]): Master list of frequency choices.
    """
    with expense_tab:
        st.subheader('Expenses')

        for category in expense_categories:
            df_cat = budget_data.loc[
                budget_data['Category'] == category
                ].copy()
            total = df_cat['Amount'].sum().round(0)
            category_emoji = df_cat['Category Emoji'].iloc[0]

            with st.expander(
                    label=f'{category_emoji} {category} – ${total:,.0f}',
                    expanded=False,
            ):
                # column width ratios
                col_widths = [1, 1, 1, 1, 2]

                # one form per expense
                for _, row in df_cat.iterrows():
                    form_key = f'form-{int(row["ID"])}'
                    with st.form(key=form_key):
                        cols = st.columns(col_widths)

                        # 1) Name
                        name_input = cols[0].text_input(
                            label='Expense',
                            value=row['Name'],
                            key=f'name-{row["ID"]}',
                        )

                        # 2) Amount
                        amount_val = float(row['Amount'])
                        step_size = float(compute_step(amount_val))
                        amount_input = cols[1].number_input(
                            label='Amount',
                            value=amount_val,
                            step=step_size,
                            format='%0.2f',
                            key=f'amount-{row["ID"]}',
                        )

                        # 3) Frequency
                        try:
                            freq_idx = frequency_options.index(row['Frequency'])
                        except ValueError:
                            freq_idx = 0
                        frequency_input = cols[2].selectbox(
                            label='Frequency',
                            options=frequency_options,
                            index=freq_idx,
                            key=f'freq-{row["ID"]}',
                        )

                        # 4) Last Updated
                        last_date = datetime.datetime.strptime(
                            row['Date'], '%m/%d/%Y'
                        ).date()
                        date_input = cols[3].date_input(
                            label='Last Updated',
                            value=last_date,
                            key=f'date-{row["ID"]}',
                        )

                        # 5) Notes
                        note_text = '' if pd.isna(row['Notes']) else row['Notes']
                        notes_input = cols[4].text_area(
                            label='Notes',
                            value=note_text,
                            key=f'notes-{row["ID"]}',
                            height=68,
                        )

                        # 6) & 7) Save / Delete
                        save_delete_cols = st.columns([1, 1])
                        save = save_delete_cols[0].form_submit_button('💾 Save', use_container_width=True)
                        delete = save_delete_cols[1].form_submit_button('❌ Delete', use_container_width=True)

                        if save:
                            save_expense(
                                expense_id=int(row['ID']),
                                name=name_input,
                                amount=amount_input,
                                frequency=frequency_input,
                                last_updated=date_input,
                                notes=notes_input,
                            )
                        if delete:
                            delete_expense(expense_id=int(row['ID']))

                # add-new-expense button
                if st.button(
                        '➕ Add Expense',
                        key=f'add-expense-{category}',
                ):
                    st.info(f'Adding new expense to {category}')


budget_data = pd.read_csv('data/budget_data.csv')

# after you've done pd.read_csv(...)
budget_data['Category Emoji'] = (
    budget_data['Category Emoji']
    # first ensure it's a str (it probably already is)
    .astype(str)
    # encode to bytes so Python will treat backslashes as escapes
    .str.encode('utf-8')
    # then decode those escapes into actual codepoints
    .str.decode('unicode_escape')
)

expense_categories = budget_data['Category'].unique().tolist()

frequency_options = budget_data['Frequency'].unique().tolist()

st.title("Budget Tracker")

# Custom CSS
st.markdown("""
<style>
    .stButton > button {
        width: 100%;
    }

    .category-header {
        background-color: #f0f0f0;
        padding: 10px;
        border-radius: 5px;
        margin-bottom: 10px;
    }

    hr {
        margin-top: 0.5rem;
        margin-bottom: 0.5rem;
    }
</style>
""", unsafe_allow_html=True)

# Main content
# Create tabs for different sections
summary_tab, statistics_tab, expense_tab, settings_tab = st.tabs(['Summary', 'Statistics', 'Expenses', 'Settings'])

with summary_tab:
    st.subheader('Summary')

    st.dataframe(budget_data)

render_expenses_tab(
    expense_tab=expense_tab,
    budget_data=budget_data,
    expense_categories=expense_categories,
    frequency_options=frequency_options,
)

st.button('➕ Add Expense Category', key=f'add-expense-category')

# with expense_tab:
#     st.subheader('Expenses')
#
#     for category in expense_categories:
#
#         category_total = budget_data.loc[budget_data['Category'] == category, 'Amount'].sum().round(0)
#
#         with st.expander(
#                 label=f'{category} - ${category_total:.0f}',
#                 expanded=False,
#         ):
#             for expense in budget_data.loc[budget_data['Category'] == category, 'Name']:
#                 st.write(expense)

# # Initialize session state for storing expenses if not present
# if "expenses" not in st.session_state:
#     st.session_state.expenses = []
#
# # Form to add a new expense
# with st.form(key="expense_form"):
#     category = st.text_input("Category", placeholder="e.g., Food, Rent, Entertainment")
#     amount = st.number_input("Amount", min_value=0.0, format="%.2f", step=1.0)
#     notes = st.text_area("Notes (optional)", placeholder="Add any relevant details here")
#     submitted = st.form_submit_button("Add Expense")
#
#     if submitted:
#         if category and amount > 0:
#             st.session_state.expenses.append({"category": category, "amount": amount, "notes": notes})
#             st.success(f"Added expense to category '{category}'!")
#         else:
#             st.error("Category and amount are required fields!")
#
# # Display expenses summary grouped by category
# if st.session_state.expenses:
#     st.markdown("### Expense Summary")
#     expenses_by_category = {}
#     for expense in st.session_state.expenses:
#         if expense["category"] not in expenses_by_category:
#             expenses_by_category[expense["category"]] = 0
#         expenses_by_category[expense["category"]] += expense["amount"]
#
#     for category, total in expenses_by_category.items():
#         st.markdown(f"- **{category}:** ${total:.2f}")
