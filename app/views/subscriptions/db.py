import datetime
from pathlib import Path
from typing import Any, Dict, Optional
from typing import Union

import pandas as pd
import streamlit as st


def st_append_to_dataframe(
        append_data: Union[Dict[str, Any], pd.Series, pd.DataFrame],
        df_name: str,
        existing_df: Optional[pd.DataFrame] = None,
        ignore_index: bool = True,
) -> None:
    """
    Appends one or more rows to a DataFrame in Streamlit’s session state.

    Args:
        append_data (Union[Dict[str, Any], pd.Series, pd.DataFrame]):
            Data to append:
            - If dict: treated as a single row.
            - If Series: converted to a single-row DataFrame.
            - If DataFrame: appended as-is.
        df_name (str): The session-state key under which to store the updated DataFrame.
        existing_df (Optional[pd.DataFrame]):
            An existing DataFrame to append to. If None, loads from `st.session_state[df_name]`.
        ignore_index (bool):
            If True, resets the index of the concatenated DataFrame to a continuous integer index.
            Defaults to True.

    Raises:
        TypeError:
            If `append_data` is not a dict, pd.Series, or pd.DataFrame.

    Returns:
        None
    """
    # Load or copy the base DataFrame
    if existing_df is None:
        df = getattr(st.session_state, df_name, pd.DataFrame())
    else:
        df = existing_df.copy()

    # Convert append_data into a DataFrame
    if isinstance(append_data, dict):
        append_df = pd.DataFrame([append_data])
    elif isinstance(append_data, pd.Series):
        append_df = append_data.to_frame().T
    elif isinstance(append_data, pd.DataFrame):
        append_df = append_data.copy()
    else:
        raise TypeError(
            f'`append_data` must be dict, pd.Series, or pd.DataFrame, got {type(append_data)}'
        )

    # Concatenate and optionally reset index
    updated_df = pd.concat(
        [df, append_df],
        ignore_index=ignore_index,
    )

    # Store updated DataFrame back into session state
    setattr(st.session_state, df_name, updated_df)


def st_save_df_to_csv(
        filename: str,
        directory: Union[str, Path] = Path('data'),
        index: bool = False,
) -> None:
    """
    Persist a session-state DataFrame to a CSV file using pathlib.

    Args:
        filename (str): Key of the DataFrame in `st.session_state` to save, and the base name of the file.
        directory (Union[str, Path]): Directory in which to save the CSV file. Defaults to 'data'.
            If the directory does not exist, it will be created.
        index (bool): Whether to write row names (index). Defaults to False.

    Raises:
        KeyError: If `filename` is not found in `st.session_state`.
        TypeError: If the object under `st.session_state[filename]` is not a DataFrame.

    Returns:
        None
    """
    # Build the full file path
    dir_path = Path(directory)
    file_path = dir_path / filename

    # Ensure .csv extension
    if file_path.suffix.lower() != '.csv':
        file_path = file_path.with_suffix('.csv')

    # Create directory if needed
    file_path.parent.mkdir(parents=True, exist_ok=True)

    # Retrieve DataFrame
    try:
        df = getattr(st.session_state, filename)
    except AttributeError:
        raise KeyError(f"No DataFrame found in session_state under key filename: '{filename}'")

    if not isinstance(df, pd.DataFrame):
        raise TypeError(f"Object under session_state['{filename}'] is not a DataFrame")

    # Save DataFrame to CSV
    df.to_csv(
        file_path,
        index=index,
        encoding='utf-8-sig',
    )


def add_subscription() -> None:
    """
    Append a blank expense for the given category and rerun to show the form.

    Args:
        category (str): Expense category.

    Returns:
        None
    """
    df = st.session_state.subscriptions.copy()
    new_id = int(df['ID'].max() + 1) if not df.empty else 1

    new_row = {
        'ID': new_id,
        'Date': datetime.date.today(),
        'Name': 'New Expense',
        'Amount': 0.0,
        'Frequency': 'Monthly',
        'Tax Deductible': False,
        'Notes': '',
        'Status': 'Active',
    }

    st_append_to_dataframe(
        append_data=new_row,
        df_name='subscriptions',
        ignore_index=True,
    )
    st_save_df_to_csv()
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
