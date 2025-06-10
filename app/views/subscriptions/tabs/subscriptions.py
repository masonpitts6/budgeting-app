from datetime import datetime
from typing import (List)

import pandas as pd
import streamlit as st
from app.config import FREQUENCIES

from app.views.budget.db import (
    save_expense,
    delete_expense,
    add_expense,
)
from app.views.budget.utils import compute_step


def render_subscriptions_tab(
        subscription_data,
        frequency_options: List[str] = FREQUENCIES,
) -> None:
    """
    Render the Subscriptions tab.

    Args:
        subscription_data (pd.DataFrame): .
        frequency_options (List[str]): List of frequency options.

    Returns:
        None
    """

    st.subheader('Subscriptions')

    cols_layout = [1, 1, 1, 1, 2]

    for _, row in subscription_data.iterrows():
        key = f'form-{int(row['ID'])}'
        with st.form(key=key):
            st.write(f'#### {row['Subscription/ Recurring Expense']}')
            cols = st.columns(cols_layout)

            name_input = cols[0].text_input(
                'Subscription/ Recurring Expense',
                value=row['Subscription/ Recurring Expense'],
                key=f'name-{row.ID}',
            )

            step = float(compute_step(float(row.Amount)))
            amount_input = cols[1].number_input(
                'Amount ($)',
                value=float(row['Amount']),
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

            notes_input = cols[4].text_area(
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
                    notes=notes_input,
                )
            if delete_btn:
                delete_expense(int(row.ID))

    if st.button('➕ Add Expense', key=f'add-{'test'}', use_container_width=True):
        add_expense('test')
