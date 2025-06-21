from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Dict

import pandas as pd

# ────────────────────────────────────────────────────────────────────────────────
# Shared helpers
# ────────────────────────────────────────────────────────────────────────────────

PERIOD_MAP: Dict[str, float] = {
    'Weekly': 52,
    'Semi-Monthly': 24,
    'Monthly': 12,
    'Quarterly': 4,
    'Annual': 1,
}


def _read_csv(file_name: str, *, data_dir: str | Path = 'data') -> pd.DataFrame:
    """
    Load a CSV file with UTF-8-SIG encoding (preserves emojis).

    Args:
        file_name: The CSV name, e.g. ``'income.csv'``.
        data_dir: Directory containing the file.

    Returns:
        DataFrame with raw data.
    """
    path = Path(data_dir) / file_name
    return pd.read_csv(path, encoding='utf-8-sig')


def _add_frequency_cols(
        df: pd.DataFrame,
        *,
        amount_col: str,
        frequency_col: str,
        annual_col: str,
) -> pd.DataFrame:
    """
    Add an annualised column plus one column per period in ``PERIOD_MAP``.

    Args:
        df: Original DataFrame.
        amount_col: Monetary column name.
        frequency_col: Frequency label column.
        annual_col: Name for the derived annual figure.

    Returns:
        DataFrame with the new columns; original columns left intact.
    """
    out = df.copy()

    out[annual_col] = (
        out[frequency_col]
        .map(PERIOD_MAP)
        .astype(float)
        * out[amount_col].astype(float)
    )

    for period, mult in PERIOD_MAP.items():
        out[period] = out[annual_col] / mult

    return out

# ────────────────────────────────────────────────────────────────────────────────
# Domain objects
# ────────────────────────────────────────────────────────────────────────────────


@dataclass(frozen=True, slots=True)
class Income:
    """
    Salary/bonus model with convenient derived properties.
    """

    table: pd.DataFrame

    # ── Properties ────────────────────────────────────────────────────────────
    @property
    def salary_pre_tax(self) -> float:
        return self.table['Annual Salary'].sum()

    @property
    def salary_taxes(self) -> float:
        return (
            self.table['Annual Salary']
            * self.table['Salary Effective Tax Rate']
        ).sum()

    @property
    def salary_post_tax(self) -> float:
        return self.salary_pre_tax - self.salary_taxes

    @property
    def bonus_pre_tax(self) -> float:
        return self.table['Bonus'].sum()

    @property
    def bonus_taxes(self) -> float:
        return (
            self.table['Bonus']
            * self.table['Total Compensation Effective Tax Rate']
        ).sum()

    @property
    def bonus_post_tax(self) -> float:
        return self.bonus_pre_tax - self.bonus_taxes

    @property
    def total_comp_pre_tax(self) -> float:
        return self.salary_pre_tax + self.bonus_pre_tax

    @property
    def total_taxes(self) -> float:
        return self.salary_taxes + self.bonus_taxes

    @property
    def total_comp_post_tax(self) -> float:
        return self.total_comp_pre_tax - self.total_taxes

    # ── Factories ────────────────────────────────────────────────────────────
    @classmethod
    def from_csv(
            cls,
            file_name: str = 'income.csv',
            *,
            data_dir: str | Path = 'data',
    ) -> 'Income':
        raw = _read_csv(file_name, data_dir=data_dir)

        enriched = _add_frequency_cols(
            raw,
            amount_col='Salary',
            frequency_col='Frequency',
            annual_col='Annual Salary',
        )

        # Bonus is already annual; keep it unchanged.
        return cls(table=enriched)


@dataclass(frozen=True, slots=True)
class Expenses:
    """
    Container for ordinary expenses.
    """

    table: pd.DataFrame

    @property
    def annual_total(self) -> float:
        return self.table['Annual Amount'].sum()

    @classmethod
    def from_csv(
            cls,
            file_name: str = 'budget_data.csv',
            *,
            data_dir: str | Path = 'data',
    ) -> 'Expenses':
        raw = _read_csv(file_name, data_dir=data_dir)

        enriched = _add_frequency_cols(
            raw,
            amount_col='Amount',
            frequency_col='Frequency',
            annual_col='Annual Amount',
        )

        return cls(table=enriched)


@dataclass(frozen=True, slots=True)
class Subscriptions(Expenses):
    """
    Same structure as Expenses but kept separate for clarity/expansion.
    """

    @classmethod
    def from_csv(
            cls,
            file_name: str = 'subscriptions.csv',
            *,
            data_dir: str | Path = 'data',
    ) -> 'Subscriptions':
        raw = _read_csv(file_name, data_dir=data_dir)

        enriched = _add_frequency_cols(
            raw,
            amount_col='Amount',
            frequency_col='Frequency',
            annual_col='Annual Amount',
        )
        return cls(table=enriched)


@dataclass(frozen=True, slots=True)
class PlannedPurchases(Expenses):
    """
    Large purchases amortised over a chosen schedule.
    """

    @classmethod
    def from_csv(
            cls,
            file_name: str = 'planned_purchases.csv',
            *,
            data_dir: str | Path = 'data',
    ) -> 'PlannedPurchases':
        raw = _read_csv(file_name, data_dir=data_dir)

        enriched = _add_frequency_cols(
            raw,
            amount_col='Cost',
            frequency_col='Amortization Method',
            annual_col='Annual Amount',
        )
        return cls(table=enriched)


@dataclass(frozen=True, slots=True)
class Budget:
    """
    High-level aggregation of all cash-flow components.
    """

    income: Income
    expenses: Expenses
    subscriptions: Subscriptions
    planned_purchases: PlannedPurchases

    # ── Derived metrics ──────────────────────────────────────────────────────
    @property
    def total_expense(self) -> float:
        return (
            self.expenses.annual_total
            + self.subscriptions.annual_total
            + self.planned_purchases.annual_total
        )

    @property
    def annual_surplus(self) -> float:
        return self.income.total_comp_post_tax - self.total_expense

    # ── Factory ─────────────────────────────────────────────────────────────
    @classmethod
    def from_csv_folder(cls, data_dir: str | Path = 'data') -> 'Budget':
        return cls(
            income=Income.from_csv(data_dir=data_dir),
            expenses=Expenses.from_csv(data_dir=data_dir),
            subscriptions=Subscriptions.from_csv(data_dir=data_dir),
            planned_purchases=PlannedPurchases.from_csv(data_dir=data_dir),
        )
