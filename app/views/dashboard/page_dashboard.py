import plotly.express as px
import streamlit as st

from app import pages
from app.views.dashboard.models import Budget

st.title(pages.dashboard_page.title)


@st.cache_data
def load_budget() -> Budget:
    return Budget.from_csv_folder('data')


budget = load_budget()


# ── Top metrics ──────────────────────────────────────────────────────────────
# ── Helpers ────────────────────────────────────────────────────────────────
def money(x: float) -> str:
    return f'${x:,.0f}'


def surplus_delta(val: float) -> str:
    return money(abs(val)) if val else ''


# ── 3 : 1 split ─────────────────────────────────────────────────────────────
left_col, right_col = st.columns([3, 1], gap='large')

# ────────────────────────────────────────────────────────────────────────────
# LEFT  ▸  Income container
# ────────────────────────────────────────────────────────────────────────────
with left_col:
    with st.container(border=True):
        st.markdown('### Income')

        income_cols = {
            'Salary': (
                budget.income.salary_pre_tax,
                budget.income.salary_taxes,
                budget.income.salary_post_tax,
            ),
            'Bonus': (
                budget.income.bonus_pre_tax,
                budget.income.bonus_taxes,
                budget.income.bonus_post_tax,
            ),
            'Total Comp': (
                budget.income.total_comp_pre_tax,
                budget.income.total_taxes,
                budget.income.total_comp_post_tax,
            ),
        }

        subcols = st.columns(len(income_cols))
        for col, (hdr, vals) in zip(subcols, income_cols.items()):
            pre, tax, post = vals
            col.metric(f'{hdr} (Pre-Tax)', money(pre))
            col.metric(f'{hdr} Taxes', money(tax))
            col.metric(f'{hdr} (After)', money(post))

# ────────────────────────────────────────────────────────────────────────────
# RIGHT ▸  Budget container
# ────────────────────────────────────────────────────────────────────────────
with right_col:
    with st.container(border=True):
        st.markdown(
            '### Budget',
        )

        st.metric('Total Comp (After Tax)',
                  money(budget.income.total_comp_post_tax))

        st.metric('Total Annual Expense',
                  money(budget.total_expense))

        surplus = budget.annual_surplus
        st.metric(
            label='Annual Surplus',
            value=money(surplus),
        )

# ── Raw tables ────────────────────────────────────────────────────
t1, t2, t3, t4 = st.tabs(['Expenses', 'Subscriptions', 'Planned Purchases', 'Income'])

with t1:
    import pandas as pd
    import plotly.express as px
    import streamlit as st

    # ----------------------------------------------------------------------
    # 1) Pull the raw table once (whatever object you already have)
    # ----------------------------------------------------------------------
    exp_df: pd.DataFrame = budget.expenses.table

    # Ensure the key columns exist
    required_cols = {'Super Category', 'Category', 'Annual'}
    missing = required_cols - set(exp_df.columns)
    if missing:
        st.error(f'Missing columns: {missing}')
        st.stop()


    # ----------------------------------------------------------------------
    # 2) Helper to build a pie with % + $ on label & hover
    # ----------------------------------------------------------------------
    def make_pie(
            df: pd.DataFrame,
            label_col: str,
            value_col: str = 'Annual',
            *,
            text_size: int = 14,  # tweak these two knobs if you like
    ):
        fig = px.pie(
            df,
            names=label_col,
            values=value_col,
        )

        fig.update_traces(
            texttemplate=(
                '<b>%{label}</b><br>'  # <b> makes label itself bold
                '%{percent:.1%}<br>'
                '$%{value:,.0f}'
            ),
            textfont=dict(size=text_size),  # ← bigger/bolder slice text
            hovertemplate=(
                '<b>%{label}</b><br>'
                'Share of total&nbsp;: %{percent:.1%}<br>'
                'Annual cost&nbsp;&nbsp;&nbsp;: $%{value:,.0f}<extra></extra>'
            ),
        )

        fig.update_layout(
            showlegend=False,
            margin=dict(t=40, l=0, r=0, b=80),
            font=dict(size=text_size),  # global font size (tooltips, etc.)
            hoverlabel=dict(font_size=text_size + 4),  # 🔧 tooltip font bump
        )

        return fig


    # 3) Aggregate for super-categories and for categories *within 'Essentials'*
    # ----------------------------------------------------------------------
    super_df = (
        exp_df
        .groupby('Super Category', as_index=False)['Annual']
        .sum()
    )

    essentials_only = exp_df[
        exp_df['Super Category']
        .str.contains('Essentials', case=False, na=False)  # ← substring, case-insensitive
    ]

    cat_df = (
        essentials_only
        .groupby('Category', as_index=False)['Annual']
        .sum()
    )

    # 4) Render pies side-by-side
    # ----------------------------------------------------------------------
    left_col, right_col = st.columns(2)

    with left_col:
        st.subheader('Budget by Super Category')
        st.plotly_chart(
            make_pie(super_df, 'Super Category'),
            use_container_width=True,
        )

    with right_col:
        st.subheader('Essentials — Breakdown by Category')
        st.plotly_chart(
            make_pie(cat_df, 'Category'),
            use_container_width=True,
        )

    st.divider()
    st.dataframe(budget.expenses.table)

with t2:
    # ── Aggregate spend per subscription ────────────────────────────────────────
    src = (
        budget.subscriptions.table
        .groupby('Subscription/ Recurring Expense', as_index=False)['Annual']
        .sum()
    )

    fig = px.treemap(
        src,
        path=['Subscription/ Recurring Expense'],
        values='Annual',
        title='Annual spend by subscription',
    )

    # ── Show % of total + $ value on both label and hover ──────────────────────
    fig.update_traces(
        # Tile label (visible on the chart)
        texttemplate=(
            '%{label}<br>'
            '%{percentRoot:.1%}<br>'  # % of grand total
            '$%{value:,.0f}'  # dollar amount
        ),

        # Hover tooltip
        hovertemplate=(
            '<b>%{label}</b><br>'
            'Share of total: %{percentRoot:.1%}<br>'
            'Annual cost: $%{value:,.0f}<extra></extra>'
        ),
    )

    st.plotly_chart(fig, use_container_width=True)

    st.dataframe(budget.subscriptions.table)

t3.dataframe(budget.planned_purchases.table)
t4.dataframe(budget.income.table)




