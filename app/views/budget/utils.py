import math
import pandas as pd
from typing import List, Optional, Union


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

from pandas.io.formats.style import Styler
def style_budget_plan_df(
        df: pd.DataFrame,
        float_cols: list[str],
        percentage_cols: List[str],
        cmap: str = 'RdYlGn_r',
) -> Styler:
    """
    Apply Excel‐style conditional formatting and percentage formatting to specified columns.

    Args:
        df (pd.DataFrame): The input DataFrame.
        percentage_cols (List[str]): List of column names in `df` whose values range from 0 to 100 and should be treated as percentages.
        cmap (str): The matplotlib colormap name for the background gradient. Defaults to 'RdYlGn'.

    Returns:
        pd.io.formats.style.Styler: A Styler object with conditional formatting and percentage formatting applied.
    """
    # Verify that all specified columns exist
    missing = [col for col in percentage_cols + float_cols if col not in df.columns]
    if missing:
        raise KeyError(f'The following columns were not found in the DataFrame: {missing}')

    # Create a copy of the DataFrame to avoid modifying the original
    df_copy = df.copy()

    # Build a formatter dict for .format()
    fmt_dict: dict[str, str] = {
        col: '{:.2f}%' for col in percentage_cols
    }

    for col in float_cols:
        fmt_dict[col] = '${:,.2f}'

    # Initialize Styler
    styler = df_copy.style

    # Apply percentage formatting
    styler = styler.format(fmt_dict)

    for col in percentage_cols:
        # Apply a background gradient only to percentage columns
        styler = styler.background_gradient(
            subset=col,
            cmap=cmap,
            vmin=df_copy[col].min(),
            vmax=df_copy[col].max(),
        )

    return styler
