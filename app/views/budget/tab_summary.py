from typing import Dict

import pandas as pd
import streamlit as st


def display_budget_summary_metrics(
        budget_plan: pd.DataFrame,
        period_map: Dict[str, float],
        annual_amount_col: str = 'Annual Amount',
) -> None:
    """
    Displays summary metrics in Streamlit for each period defined in period_map,
    calculating the total annual budget divided by each period's divisor.

    Args:
        budget_plan (pd.DataFrame): DataFrame containing an 'Annual Amount' column.
        period_map (Dict[str, float]): Dictionary mapping period names (e.g., 'Weekly',
            'Monthly', etc.) to their corresponding divisors.
    """
    total_annual = budget_plan[annual_amount_col].sum()
    cols = st.columns(len(period_map))

    for idx, period in enumerate(period_map.keys()):
        with cols[idx]:
            st.write(f'### {period}')
            st.metric(
                label='',
                value=f'${total_annual / period_map[period]:,.0f}',
            )

import pandas as pd
import streamlit as st
from typing import Dict


def display_budget_dataframe(
        budget_plan: pd.DataFrame,
        period_map: Dict[str, float],
) -> None:
    """
    Displays a styled DataFrame in Streamlit, showing only the specified columns
    ('Date', 'Category', 'Name', all periods from period_map, and '% of Total Budget'),
    with currency formatting for period columns and percentage formatting for '% of Total Budget'.

    Args:
        budget_plan (pd.DataFrame): DataFrame containing at least the columns 'Date',
            'Category', 'Name', each period key in period_map, and '% of Total Budget'.
        period_map (Dict[str, float]): Dictionary whose keys correspond to period columns
            in budget_plan (e.g., 'Weekly', 'Monthly', etc.).
    """
    # ─── Slice off only the columns to display ────────────────────────────────────
    display_cols = [
        'Date',
        'Category',
        'Name',
    ] + list(period_map.keys()) + [
        '% of Total Budget',
    ]
    display_df = budget_plan.loc[:, display_cols]

    # ─── Define formatting for each column ───────────────────────────────────────
    df_fmt = {
        col: '${:,.2f}'
        for col in period_map.keys()
    }
    df_fmt['% of Total Budget'] = '{:.2f}%'

    # ─── Apply styling and render in Streamlit ──────────────────────────────────
    styled = display_df.style.format(df_fmt)
    st.dataframe(
        styled,
        use_container_width=True,
        hide_index=True,
    )
