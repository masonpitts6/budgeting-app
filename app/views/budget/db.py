import datetime
from typing import Dict, List, Tuple

import pandas as pd
import streamlit as st


def add_expense(category: str) -> None:
    """
    Append a blank expense for the given category and rerun to show the form.

    Args:
        category (str): Expense category.

    Returns:
        None
    """
    # Keeps expander of the category of the added expense open.
    st.session_state[f'exp_{category}'] = True

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

    # Keeps expander of the category of the saved expense open.
    category_of_that_id = df.loc[df['ID'] == expense_id, 'Category'].iloc[0]
    st.session_state[f'exp_{category_of_that_id}'] = True
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

    # Keeps expander of the category of the deleted expense open.
    category_of_that_id = df.loc[df['ID'] == expense_id, 'Category'].iloc[0]
    st.session_state[f'exp_{category_of_that_id}'] = True

    df = df[df['ID'] != expense_id].reset_index(drop=True)
    st.session_state.budget_data = df

    _save_df()

    st.warning(f'Deleted expense {expense_id}')
    st.rerun()


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


def bootstrap_budget_data(
        period_map: Dict[str, float],
        filepath: str = 'data/budget_data.csv',
) -> Tuple[pd.DataFrame, pd.DataFrame, List[str], List[str]]:
    """
    Initializes session state for budget data, computes derived budget_plan,
    and returns budget_plan along with unique expense categories and frequency options.

    Args:
        period_map (Dict[str, float]): Dictionary mapping frequency names to
            their corresponding annual-multiplier (e.g., {'Monthly': 12, 'Weekly': 52}).
        filepath (str): Path to the CSV file to load budget data from. Defaults to 'data/budget_data.csv'.

    Returns:
        Tuple[pd.DataFrame, List[str], List[str]]:
            - budget_data: DataFrame containing original data.
            - budget_plan: DataFrame containing original data plus 'Annual Amount',
              period columns, and '% of Total Budget'.
            - expense_categories: List of unique non-null categories from the original data.
            - frequency_options: List of unique non-null frequency values from the original data.
    """
    # ─── Load or initialize session_state.budget_data ───────────────────────────
    if 'budget_data' not in st.session_state:
        try:
            st.session_state.budget_data = pd.read_csv(
                filepath,
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

    # ─── Create budget_plan and compute 'Annual Amount' ─────────────────────────
    budget_plan = st.session_state.budget_data.copy()
    budget_plan['Annual Amount'] = (
            budget_plan['Frequency']
            .fillna('Monthly')
            .map(period_map)
            .fillna(0)
            .astype(int)
            * budget_plan['Amount']
    )

    # ─── Compute per-period columns based on period_map ─────────────────────────
    for period in period_map.keys():
        budget_plan[period] = budget_plan['Annual Amount'] / period_map[period]

    # ─── Compute percentage of total budget ─────────────────────────────────────
    total_annual = budget_plan['Annual Amount'].sum()
    budget_plan['% of Total Budget'] = (
        budget_plan['Annual Amount'] / total_annual * 100
        if total_annual != 0 else 0
    )

    # ─── Extract unique non-null categories and frequencies ──────────────────────
    expense_categories = (
        st.session_state.budget_data['Category']
        .dropna()
        .unique()
        .tolist()
    )
    frequency_options = (
        st.session_state.budget_data['Frequency']
        .dropna()
        .unique()
        .tolist()
    )

    return st.session_state.budget_data, budget_plan, expense_categories, frequency_options
