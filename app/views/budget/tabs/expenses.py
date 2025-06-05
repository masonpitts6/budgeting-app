from datetime import datetime
from typing import (List)

import pandas as pd
import streamlit as st
from streamlit.delta_generator import DeltaGenerator

from app.views.budget.db import (
    save_expense,
    delete_expense,
    add_expense,
)
from app.views.budget.utils import compute_step


def render_expenses_tab(
        budget_data,
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

    st.subheader('Expenses')

    for category in expense_categories:
        df_cat = budget_data[budget_data['Category'] == category]
        total = df_cat['Amount'].sum().round(0)

        # Look up the “expanded” flag in session_state
        exp_key = f"exp_{category}"
        expanded_flag = st.session_state.get(exp_key, False)

        with st.expander(
                f'{category} – ${total:,.0f} / Month',
                expanded=expanded_flag,
        ):
            cols_layout = [1, 1, 1, 1, 1, 0.5, 2]

            for _, row in df_cat.iterrows():
                key = f'form-{int(row.ID)}'
                with st.form(key=key):
                    st.write(f'#### {row['Name']}')
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

                    tax_input = cols[4].selectbox(
                        label='Tax Deductible',
                        index=0 if row['Tax Deductible'] else 1,
                        options=[
                            'Yes',
                            'No',
                        ],
                        key=f'tax-{row.ID}',
                    )

                    color_input = cols[5].color_picker(
                        label='Color',
                    )

                    notes_input = cols[6].text_area(
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
        '➕ Create a new expense category',
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
