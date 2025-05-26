import datetime
import math
from typing import List

import pandas as pd
import streamlit as st
from streamlit.delta_generator import DeltaGenerator
import streamlit as st
import pandas as pd
from typing import Dict, List
from pandas.io.formats.style import Styler
from app import pages

def compute_step(amount: float) -> int:
    """
    Compute a step size that’s the nearest smaller power of ten for the given amount.
    For example:
        - 7.25 → 0.1
        - 42.50 → 1
        - 327 → 10
        - 2300 → 100

    Args:
        amount (float): The expense amount.

    Returns:
        int: The step size, calculated as 10 raised to the power of the floor of the log10 of the amount minus one.
             Returns 1 if the amount is less than or equal to 0.
    """
    if amount <= 0:
        return 1
    exponent = math.floor(math.log10(amount))
    return 10 ** max(exponent - 1, 0)


import datetime
import math
from typing import List

import pandas as pd
import streamlit as st
from streamlit.delta_generator import DeltaGenerator

# --- Session State Bootstrap ------------------------------------------------
if 'budget_data' not in st.session_state:
    try:
        st.session_state.budget_data = pd.read_csv(
            'data/budget_data.csv',
            encoding='utf-8-sig',
        )
    except FileNotFoundError:
        st.session_state.budget_data = pd.DataFrame(
            columns=[
                'ID',
                'Date',
                'Category',
                'Name',
                'Amount',
                'Frequency',
                'Tax Deductible',
                'Notes',
                'Status',
            ]
        )


def _save_df() -> None:
    """
    Persist session-state DataFrame to CSV.

    Returns:
        None
    """
    st.session_state.budget_data.to_csv(
        'data/budget_data.csv',
        index=False,
        encoding='utf-8-sig',
    )


def compute_step(amount: float) -> int:
    """
    Compute a step size that’s the nearest smaller power of ten for the given amount.

    Args:
        amount (float): The expense amount.

    Returns:
        int: The step size (10^(floor(log10(amount)) - 1)), minimum 1.
    """
    if amount <= 0:
        return 1
    exponent = math.floor(math.log10(amount))
    return 10 ** max(exponent - 1, 0)


def add_expense(category: str) -> None:
    """
    Append a blank expense for the given category and rerun to show the form.

    Args:
        category (str): Expense category.

    Returns:
        None
    """
    df = st.session_state.budget_data.copy()
    new_id = int(df['ID'].max() + 1) if not df.empty else 1

    new_row = {
        'ID': new_id,
        'Date': datetime.date.today(),
        'Category': category,
        'Name': 'New Expense',
        'Amount': 0.0,
        'Frequency': 'Monthly',
        'Tax Deductible': False,
        'Notes': '',
        'Status': 'Active',
    }

    df = pd.concat(
        [df, pd.DataFrame([new_row])],
        ignore_index=True,
    )
    st.session_state.budget_data = df
    _save_df()
    st.rerun()


def save_expense(
        expense_id: int,
        name: str,
        amount: float,
        frequency: str,
        last_updated: datetime.date,
        tax_deductible: bool,
        notes: str,
        status: str = 'Active',
) -> None:
    """
    Update an existing expense and persist changes.

    Args:
        expense_id (int): ID of the expense.
        name (str): Expense name.
        amount (float): Expense amount.
        frequency (str): Frequency value.
        last_updated (date): Last updated date.
        tax_deductible (bool): Tax deductible flag.
        notes (str): Notes text.
        status (str): Expense status.

    Returns:
        None
    """
    df = st.session_state.budget_data.copy()
    mask = df['ID'] == expense_id
    df.loc[mask, 'Name'] = name
    df.loc[mask, 'Amount'] = amount
    df.loc[mask, 'Frequency'] = frequency
    df.loc[mask, 'Date'] = last_updated
    df.loc[mask, 'Tax Deductible'] = tax_deductible
    df.loc[mask, 'Notes'] = notes
    df.loc[mask, 'Status'] = status

    st.session_state.budget_data = df
    _save_df()
    st.success(f'Expense {expense_id} saved!')
    st.rerun()


def delete_expense(expense_id: int) -> None:
    """
    Delete an expense by ID and persist changes.

    Args:
        expense_id (int): ID of the expense to delete.

    Returns:
        None
    """
    df = st.session_state.budget_data.copy()
    df = df[df['ID'] != expense_id].reset_index(drop=True)
    st.session_state.budget_data = df
    _save_df()

    st.warning(f'Deleted expense {expense_id}')
    st.rerun()


def render_expenses_tab(
        expense_tab: DeltaGenerator,
        expense_categories: List[str],
        frequency_options: List[str],
) -> None:
    """
    Render the Expenses tab grouping each expense in its own form.

    Args:
        expense_tab (DeltaGenerator): Container for rendering.
        expense_categories (List[str]): List of categories.
        frequency_options (List[str]): List of frequency options.

    Returns:
        None
    """
    df = st.session_state.budget_data
    with expense_tab:
        st.subheader('Expenses')

        for category in expense_categories:
            df_cat = df[df['Category'] == category]
            total = df_cat['Amount'].sum().round(0)

            with st.expander(
                    f'{category} – ${total:,.0f} / Month',
                    expanded=False,
            ):
                cols_layout = [1, 1, 1, 1, 1, 2]

                for _, row in df_cat.iterrows():
                    key = f'form-{int(row.ID)}'
                    with st.form(key=key):
                        st.write(f'#### {row.Name}')
                        cols = st.columns(cols_layout)

                        name_input = cols[0].text_input(
                            'Expense',
                            value=row.Name,
                            key=f'name-{row.ID}',
                        )

                        step = float(compute_step(float(row.Amount)))
                        amount_input = cols[1].number_input(
                            'Amount ($)',
                            value=float(row.Amount),
                            step=step,
                            format='%.2f',
                            key=f'amount-{row.ID}',
                        )

                        freq_index = (
                            frequency_options.index(row.Frequency)
                            if row.Frequency in frequency_options
                            else 0
                        )
                        freq_input = cols[2].selectbox(
                            'Frequency',
                            options=frequency_options,
                            index=freq_index,
                            key=f'freq-{row.ID}',
                        )

                        date_val = (
                            pd.to_datetime(row.Date).date()
                            if pd.notna(row.Date)
                            else datetime.date.today()
                        )
                        date_input = cols[3].date_input(
                            'Last Updated',
                            value=date_val,
                            key=f'date-{row.ID}',
                        )

                        cols[4].write('')
                        cols[4].write('')
                        tax_input = cols[4].checkbox(
                            'Tax Deductible',
                            value=row['Tax Deductible'],
                            key=f'tax-{row.ID}',
                        )

                        notes_input = cols[5].text_area(
                            'Notes',
                            value=row.Notes or '',
                            key=f'notes-{row.ID}',
                            height=68,
                        )

                        save_col, delete_col = st.columns([1, 1])
                        save_btn = save_col.form_submit_button('💾 Save', use_container_width=True)
                        delete_btn = delete_col.form_submit_button('❌ Delete', use_container_width=True)

                        if save_btn:
                            save_expense(
                                expense_id=int(row.ID),
                                name=name_input,
                                amount=amount_input,
                                frequency=freq_input,
                                last_updated=date_input,
                                tax_deductible=tax_input,
                                notes=notes_input,
                            )
                        if delete_btn:
                            delete_expense(int(row.ID))

                if st.button('➕ Add Expense', key=f'add-{category}', use_container_width=True):
                    add_expense(category)

        # --- New Category UI ----------------------------------
        new_category = st.text_input(
            '➕ Add a new expense category',
            value='',
            placeholder='e.g. Groceries',
            key='new_category_input'
        )
        if st.button(
                '🟩 Create Category',
                key='create_category_btn',
                use_container_width=True
        ):
            if new_category.strip():
                add_expense(new_category.strip())
            else:
                st.error("Please enter a valid category name.")
        st.markdown("---")  # optional divider

# --- Main Layout -------------------------------------------------------------
expense_categories = (
    st.session_state.budget_data['Category'].dropna().unique().tolist()
)
frequency_options = (
    st.session_state.budget_data['Frequency'].dropna().unique().tolist()
)

st.title(pages.budget_page.title)

tabs = st.tabs(['Summary', 'Statistics', 'Expenses', 'Settings'])
with tabs[0]:
    PERIOD_MAP = {
        'Weekly': 52,
        'Semi-Monthly': 24,
        'Monthly': 12,
        'Quarterly': 4,
        'Yearly': 1,
    }

    st.write('# Summary - Total Budget')
    budget_plan = st.session_state.budget_data.copy()
    budget_plan['Annual Amount'] = budget_plan['Frequency'].fillna('Monthly').map(PERIOD_MAP).fillna(0).astype(int) * \
                                   budget_plan['Amount']

    for period in PERIOD_MAP.keys():
        budget_plan[period] = budget_plan['Annual Amount'] / PERIOD_MAP[period]

    budget_plan['% of Total Budget'] = budget_plan['Annual Amount'] / budget_plan['Annual Amount'].sum() * 100

    cols = st.columns(5)

    with cols[0]:
        st.write('### Weekly')
        st.metric(
            label='',
            value=f"${budget_plan['Annual Amount'].sum() / PERIOD_MAP['Weekly']:,.0f}",
        )

    with cols[1]:
        st.write('### Semi-Monthly')
        st.metric(
            label='',
            value=f"${budget_plan['Annual Amount'].sum() / PERIOD_MAP['Semi-Monthly']:,.0f}",
        )

    with cols[2]:
        st.write('### Monthly')
        st.metric(
            label='',
            value=f"${budget_plan['Annual Amount'].sum() / PERIOD_MAP['Monthly']:,.0f}",
        )

    with cols[3]:
        st.write('### Quarterly')
        st.metric(
            label='',
            value=f"${budget_plan['Annual Amount'].sum() / PERIOD_MAP['Quarterly']:,.0f}",
        )

    with cols[4]:
        st.write('### Annual')
        st.metric(
            label='',
            value=f"${budget_plan['Annual Amount'].sum() / PERIOD_MAP['Yearly']:,.0f}",
        )


    def style_budget_by_category(
            df: pd.DataFrame,
            category_col: str,
            color_map: Dict[str, str],
    ) -> Styler:
        """
        Apply a background‐color to each row according to its category.

        Args:
            df (pd.DataFrame): The DataFrame you’re displaying.
            category_col (str): Name of the column containing the category.
            color_map (Dict[str, str]): Mapping from category → CSS color.

        Returns:
            Styler: A Styler with background colors applied.
        """

        def _highlight_row(row: pd.Series) -> List[str]:
            # look up the color for this row’s category (fallback to transparent)
            bg = color_map.get(row[category_col], 'transparent')
            # return one style string per column
            return [f'background-color: {bg}' for _ in row]

        return df.style.apply(
            func=_highlight_row,
            axis=1,
        )


    # ─── build your color map ───────────────────────────────────────────────────────
    color_map = {
        'Housing': '#E69F00',  # orange
        'Subscriptions & Recurring Expenses': '#56B4E9',  # sky blue
        'Planned Purchases': '#009E73',  # green
        'Utilities & Communications': '#F0E442',  # yellow
        'Insurance': '#0072B2',  # blue
        'Debt Service': '#D55E00',  # vermillion
        'Discretionary Income': '#CC79A7',  # pink
    }

    # ─── slice off only the columns you want to show ───────────────────────────────
    display_cols = ['Date', 'Category', 'Name'] + list(PERIOD_MAP.keys()) + ['% of Total Budget']
    display_df = budget_plan.loc[:, display_cols]

    # ─── style & render ────────────────────────────────────────────────────────────
    styled = style_budget_by_category(
        df=display_df,
        category_col='Category',
        color_map=color_map,
    )

    df_fmt = {col: '${:,.2f}' for col in PERIOD_MAP.keys()}
    df_fmt['% of Total Budget'] = '{:.2f}%'

    styled = styled.format(df_fmt)

    st.dataframe(styled, use_container_width=True, hide_index=True)

    for category in expense_categories:

        with st.container(border=True):
            st.write(f'# {category}')
            st.divider()

            cols = st.columns(8)

            with cols[0]:
                st.write('### Weekly Budget')
                cols[0].metric(
                    label='',
                    value=f"${budget_plan['Annual Amount'].sum() / PERIOD_MAP['Weekly']:,.0f}",
                )

            with cols[1]:
                st.write('#### Semi-Monthly Budget')
                cols[1].metric(
                    label='',
                    value=f"${budget_plan['Annual Amount'].sum() / PERIOD_MAP['Semi-Monthly']:,.0f}",
                )

            with cols[2]:
                st.write('#### Monthly Budget')
                cols[2].metric(
                    label='',
                    value=f"${budget_plan['Annual Amount'].sum() / PERIOD_MAP['Monthly']:,.0f}",
                )

            with cols[3]:
                st.write('#### Quarterly Budget')
                cols[3].metric(
                    label='',
                    value=f"${budget_plan['Annual Amount'].sum() / PERIOD_MAP['Quarterly']:,.0f}",
                )

            with cols[4]:
                st.write('#### Annual Budget')
                cols[4].metric(
                    label='',
                    value=f"${budget_plan['Annual Amount'].sum() / PERIOD_MAP['Yearly']:,.0f}",
                )

            with cols[5]:
                st.write('#### % Total Budget')
                cols[5].metric(
                    label='',
                    value=f"${budget_plan['Annual Amount'].sum() / PERIOD_MAP['Yearly']:,.0f}",
                )

            with cols[6]:
                st.write('#### % After-Tax Income')
                cols[6].metric(
                    label='',
                    value=f"${budget_plan['Annual Amount'].sum() / PERIOD_MAP['Yearly']:,.0f}",
                )

            with cols[7]:
                st.write('#### % Pre-Tax Income')
                cols[7].metric(
                    label='',
                    value=f"${budget_plan['Annual Amount'].sum() / PERIOD_MAP['Yearly']:,.0f}",
                )

            st.divider()
            st.write('## Rent')

            st.divider()

            cols = st.columns(5)

            with cols[0]:
                st.write('### Weekly Budget')
                cols[0].metric(
                    label='',
                    value=f"${budget_plan['Annual Amount'].sum() / PERIOD_MAP['Weekly']:,.0f}",
                )

            with cols[1]:
                st.write('### Semi-Monthly Budget')
                cols[1].metric(
                    label='',
                    value=f"${budget_plan['Annual Amount'].sum() / PERIOD_MAP['Semi-Monthly']:,.0f}",
                )

            with cols[2]:
                st.write('### Monthly Budget')
                cols[2].metric(
                    label='',
                    value=f"${budget_plan['Annual Amount'].sum() / PERIOD_MAP['Monthly']:,.0f}",
                )

            with cols[3]:
                st.write('### Quarterly Budget')
                cols[3].metric(
                    label='',
                    value=f"${budget_plan['Annual Amount'].sum() / PERIOD_MAP['Quarterly']:,.0f}",
                )

            with cols[4]:
                st.write('### Annual Budget')
                cols[4].metric(
                    label='',
                    value=f"${budget_plan['Annual Amount'].sum() / PERIOD_MAP['Yearly']:,.0f}",
                )

render_expenses_tab(
    expense_tab=tabs[2],
    expense_categories=expense_categories,
    frequency_options=frequency_options,
)

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
