import streamlit as st
import pandas as pd
import os
from pathlib import Path
import plotly.express as px
from app import pages

st.title(pages.income_page.title)

# Construct the correct file path
file_path = Path(os.getcwd()) / "data" / "income.csv"

# Read the CSV file
income_data = pd.read_csv(file_path)

lhs_col, rhs_col = st.columns([3, 1])

with rhs_col:
    # Initialize session state for income sources
    if "income_sources" not in st.session_state:
        st.session_state.income_sources = [1]  # Start with Income 1

    if "income_values" not in st.session_state:
        st.session_state.income_values = {}

    # Convert DataFrame column to a list for selectbox options
    job_titles = income_data["Job Title"].tolist()


    # Function to add a new income source dynamically
    def add_income_source():
        if st.session_state.income_sources:
            new_income_id = max(st.session_state.income_sources) + 1  # Get the next available number
        else:
            new_income_id = 1  # Default to 1 if all were removed
        st.session_state.income_sources.append(new_income_id)


    # Function to remove an income source
    def remove_income_source(source_id):
        if len(st.session_state.income_sources) > 1:
            # Remove selected income source while preserving order
            st.session_state.income_sources = [inc for inc in st.session_state.income_sources if inc != source_id]
            # Remove stored selection values
            selection_keys = [key for key in st.session_state.income_values if key == f"income_{source_id}"]
            for key in selection_keys:
                del st.session_state.income_values[key]


    # Function to reset income sources
    def reset_income_sources():
        st.session_state.income_sources = [1]  # Reset to only Income 1
        st.session_state.income_values = {"income_1": job_titles[0]}  # Reset to default value


    @st.dialog(title='Create Income Source')
    def create_new_income_source():

        existing_income_data = pd.read_csv(file_path)

        new_job_title = st.text_input('Job Title')
        new_salary = st.number_input('Salary', min_value=0, step=1_000)
        new_bonus = st.number_input('Bonus', min_value=0, step=1_000)
        default_tax_rate = st.number_input("Tax Rate (%)", value=30) / 100
        new_notes = st.text_area('Notes')

        save_add_cols = st.columns(2)

        with save_add_cols[0]:
            save_and_close = st.button('Save and Close')

        with save_add_cols[1]:
            save_and_add = st.button('Add Income Source')

        if save_and_close or save_and_add:
            new_income_data = pd.DataFrame(
                [
                    {
                        "Job Title": new_job_title,
                        "Salary": new_salary,
                        "Bonus": new_bonus,
                        "Total Compensation": new_salary + new_bonus,
                        "Salary Effective Tax Rate": default_tax_rate * 100,  # Convert back to percentage
                        "Total Compensation Effective Tax Rate": default_tax_rate * 100,
                        "After Tax Salary": (1 - default_tax_rate) * new_salary,
                        "After Tax Bonus": (1 - default_tax_rate) * new_bonus,
                        "After Tax Total Compensation": (1 - default_tax_rate) * (new_salary + new_bonus),
                        # "Notes": new_notes  # Include notes field
                    }
                ]
            )

            existing_income_data = pd.concat(
                [
                    existing_income_data,
                    new_income_data
                ]
            )

            existing_income_data.to_csv(file_path)

            st.rerun()


    def save_data(data):
        data.to_csv(file_path, index=False)


    @st.dialog(title="Edit Income Source")
    def edit_income_source():
        if income_data.empty:
            st.warning("No income sources available.")
            return

        selected_job = st.selectbox("Select an income source to edit:", income_data["Job Title"].unique())

        if selected_job:
            row_data = income_data[income_data["Job Title"] == selected_job].iloc[0]

            # Editable Fields
            edit_job_title = st.text_input("Job Title", value=row_data["Job Title"])
            edit_salary = st.number_input("Salary", min_value=0, step=1_000, value=int(row_data["Salary"]))
            edit_bonus = st.number_input("Bonus", min_value=0, step=1_000, value=int(row_data["Bonus"]))
            edit_tax_rate = st.number_input("Tax Rate (%)",
                                            value=float(row_data["Salary Effective Tax Rate"])) / 100
            edit_notes = st.text_area("Notes")

            update_delete_cols = st.columns(2)

            with update_delete_cols[0]:
                if st.button("💾 Save Changes"):
                    # Update DataFrame
                    income_data.loc[income_data["Job Title"] == selected_job, ["Job Title", "Salary", "Bonus",
                                                                               "Total Compensation",
                                                                               "Salary Effective Tax Rate",
                                                                               "Total Compensation Effective Tax Rate",
                                                                               "After Tax Salary",
                                                                               "After Tax Bonus",
                                                                               "After Tax Total Compensation"]] = [
                        edit_job_title, edit_salary, edit_bonus,
                        edit_salary + edit_bonus,
                        edit_tax_rate * 100, edit_tax_rate * 100,
                        (1 - edit_tax_rate) * edit_salary,
                        (1 - edit_tax_rate) * edit_bonus,
                        (1 - edit_tax_rate) * (edit_salary + edit_bonus)
                    ]
                    save_data(income_data)
                    st.success("Income source updated successfully!")
                    st.session_state.dialog_open = False  # Close dialog
                    st.rerun()

            with update_delete_cols[1]:
                if st.button("🗑️ Delete Income Source"):
                    # Remove the selected row
                    income_data.drop(income_data[income_data["Job Title"] == selected_job].index, inplace=True)
                    save_data(income_data)
                    st.success("Income source deleted successfully!")
                    st.session_state.dialog_open = False  # Close dialog
                    st.rerun()


    st.title('Tax Rates')

    cols = st.columns(2)

    with cols[0]:
        salary_tax_rate = st.number_input(label='Salary (%)', value=22) / 100
    with cols[1]:
        total_comp_tax_rate = st.number_input(label='Total Compensation (%)', value=23) / 100

    st.title('Income Sources')
    # Display select boxes with remove buttons
    for income_id in sorted(st.session_state.income_sources):  # Ensure proper ordering
        cols = st.columns([4, 1])  # Adjust column width: 4x for selectbox, 1x for button

        with cols[0]:  # Selectbox column
            default_value = st.session_state.income_values.get(f"income_{income_id}", job_titles[0])
            selected_value = st.selectbox(
                label=f"Income {income_id}",
                options=job_titles,
                index=job_titles.index(default_value) if default_value in job_titles else 0,
                key=f"income_{income_id}"
            )
            st.session_state.income_values[f"income_{income_id}"] = selected_value  # Store selection persistently

        with cols[1]:  # Remove button column
            st.markdown("<br>", unsafe_allow_html=True)  # Adds spacing
            st.button("❌", key=f"remove_{income_id}", on_click=remove_income_source, args=(income_id,),
                      use_container_width=True)

    # Create columns for buttons to align them in the same row
    button_cols = st.columns([1, 1])  # Two equal-sized columns

    with button_cols[0]:
        st.button("➕ Add", on_click=add_income_source, use_container_width=True)
        st.button("🟩 Create", on_click=create_new_income_source, use_container_width=True)

    with button_cols[1]:
        st.button("🔄 Reset", on_click=reset_income_sources, use_container_width=True)
        st.button("✏️ Edit", on_click=edit_income_source, use_container_width=True)

with lhs_col:
    incomes = list(st.session_state.income_values.values())
    incomes_df = income_data[income_data['Job Title'].isin(incomes)]

    with st.expander(label="📊 **Total Income**", expanded=True):
        st.title('Total Income')

        cols = st.columns(3)

        total_salary = incomes_df['Salary'].sum()
        after_tax_total_salary = total_salary * (1 - salary_tax_rate)
        total_bonus = incomes_df['Bonus'].sum()
        total_compensation = incomes_df['Total Compensation'].sum()
        after_tax_total_compensation = total_compensation * (1 - total_comp_tax_rate)
        after_tax_total_bonus = after_tax_total_compensation - after_tax_total_salary if after_tax_total_compensation > after_tax_total_salary else 0

        tax_salary = total_salary - after_tax_total_salary
        tax_bonus = total_bonus - after_tax_total_bonus
        tax_total_compensation = total_compensation - after_tax_total_compensation

        with cols[0]:
            st.metric(label="Salary", value=f"${total_salary:,.0f}", delta=f"-${tax_salary:,.0f}")
            st.metric(label='After Tax Salary', value=f"${after_tax_total_salary:,.0f}")

        with cols[1]:
            st.metric(label="Bonus", value=f"${total_bonus:,.0f}", delta=f"-${tax_bonus:,.0f}")
            st.metric(label='After Tax Bonus', value=f"${after_tax_total_bonus:,.0f}")

        with cols[2]:
            st.metric(label="Total Compensation", value=f"${total_compensation:,.0f}",
                      delta=f"-${tax_total_compensation:,.0f}")
            st.metric(label="After Tax Total Compensation", value=f"${after_tax_total_compensation:,.0f}")

        # **Create Two Pie Charts**
        pie_data_pre_tax = pd.DataFrame({
            "Category": ["Salary", "Bonus"],
            "Amount": [total_salary, total_bonus]
        })

        # Create category labels for Salary and Bonus
        salary_categories = [f"Salary: {income}" for income in incomes]
        bonus_categories = [f"Bonus: {income}" for income in incomes]

        # Combine categories
        income_categories = salary_categories + bonus_categories

        # Extract salary and bonus values in the correct order
        salary_values = incomes_df["Salary"].tolist()  # Salary values in order
        bonus_values = incomes_df["Bonus"].tolist()  # Bonus values in order

        # Combine values to match category order
        income_values = salary_values + bonus_values  # Ensure correct order

        pie_data_pre_tax_breakdown = pd.DataFrame(
            {
                'Category': income_categories,
                'Amount': income_values
            }
        )

        pie_data_after_tax = pd.DataFrame({
            "Category": ["After Tax Salary", "After Tax Bonus", 'Salary Tax', 'Bonus Tax'],
            "Amount": [after_tax_total_salary, after_tax_total_bonus, tax_salary, tax_bonus]
        })

        # Create category labels for After-Tax Salary and After-Tax Bonus
        after_tax_salary_categories = [f"After Tax Salary: {income}" for income in incomes]
        after_tax_bonus_categories = [f"After Tax Bonus: {income}" for income in incomes]

        # Combine categories
        after_tax_income_categories = after_tax_salary_categories + after_tax_bonus_categories

        # Extract after-tax salary and bonus values in the correct order
        after_tax_salary_values = incomes_df["After Tax Salary"].tolist()  # After-tax Salary values
        after_tax_bonus_values = incomes_df["After Tax Bonus"].tolist()  # After-tax Bonus values

        # Combine values to match category order
        after_tax_income_values = after_tax_salary_values + after_tax_bonus_values

        pie_data_after_tax_breakdown = pd.DataFrame(
            {
                'Category': after_tax_income_categories,
                'Amount': after_tax_income_values
            }
        )

        # **Generate Pie Charts**
        col1, col2 = st.columns(2)

        with col1:
            custom_colors = {
                "After Tax Salary": "#1f77b4",  # Blue
                "After Tax Bonus": "#aec7e8",  # Orange
                "Salary Tax": "#d62728",  # Green
                "Bonus Tax": "#ff9896",  # Red
            }

            fig3 = px.pie(pie_data_after_tax, names="Category", values="Amount", title="Compensation Breakdown",
                          color="Category",  # Match color mapping
                          color_discrete_map=custom_colors)
            fig3.update_layout(height=400, width=400, legend=dict(
                orientation="h",  # Horizontal legend
                yanchor="top",  # Align from the top
                y=-0.3,  # Adjust this value downward if overlapping occurs (e.g., -0.4)
                xanchor="center",
                x=0.5
            ),
                               margin=dict(t=50, b=100))
            st.plotly_chart(fig3, use_container_width=True)

        with col2:
            fig4 = px.pie(pie_data_after_tax_breakdown, names="Category", values="Amount",
                          title="After-Tax Compensation Breakdown")
            fig4.update_layout(height=400, width=400, legend=dict(
                orientation="h",  # Horizontal legend
                yanchor="top",  # Align from the top
                y=-0.3,  # Adjust this value downward if overlapping occurs (e.g., -0.4)
                xanchor="center",
                x=0.5
            ),
                               margin=dict(t=50, b=100))
            st.plotly_chart(fig4, use_container_width=True)

    for income in incomes:
        with st.expander(label=f'💸 **{income}**', expanded=True):
            st.title(income)

            income_df = income_data[income_data['Job Title'] == income]

            # Calculate metrics
            salary = income_df['Salary'].item()
            bonus = income_df['Bonus'].item()
            total_compensation = income_df['Total Compensation'].item()
            after_tax_salary = income_df['After Tax Salary'].item()
            after_tax_bonus = income_df['After Tax Bonus'].item()
            after_tax_total_compensation = income_df['After Tax Total Compensation'].item()

            # Calculate taxes
            salary_tax = salary - after_tax_salary
            bonus_tax = bonus - after_tax_bonus
            total_comp_tax = total_compensation - after_tax_total_compensation

            # Display metrics with deltas for tax impact
            cols = st.columns(3)

            with cols[0]:
                st.metric(label="Salary", value=f"${salary:,.0f}", delta=f"-${salary_tax:,.0f}")
                st.metric(label='After Tax Salary', value=f"${after_tax_salary:,.0f}")

            with cols[1]:
                st.metric(label="Bonus", value=f"${bonus:,.0f}", delta=f"-${bonus_tax:,.0f}")
                st.metric(label='After Tax Bonus', value=f"${after_tax_bonus:,.0f}")

            with cols[2]:
                st.metric(label="Total Compensation", value=f"${total_compensation:,.0f}",
                          delta=f"-${total_comp_tax:,.0f}")
                st.metric(label="After Tax Total Compensation", value=f"${after_tax_total_compensation:,.0f}")

            # Visualization - Pie Chart for Income Breakdown

            custom_colors = {
                "After Tax Salary": "#1f77b4",  # Blue
                "After Tax Bonus": "#aec7e8",  # Orange
                "Salary Tax": "#d62728",  # Green
                "Bonus Tax": "#ff9896",  # Red
            }

            pie_data_after_tax = pd.DataFrame({
                "Category": ["After Tax Salary", "After Tax Bonus", 'Salary Tax', 'Bonus Tax'],
                "Amount": [after_tax_salary, after_tax_bonus, salary_tax, bonus_tax]
            })

            fig2 = px.pie(pie_data_after_tax, names="Category", values="Amount",
                          title="Compensation Breakdown", color="Category",  # Match color mapping
                          color_discrete_map=custom_colors)
            fig2.update_layout(height=400, width=400, legend=dict(
                orientation="h",  # Horizontal legend
                yanchor="top",  # Align from the top
                y=-0.3,  # Adjust this value downward if overlapping occurs (e.g., -0.4)
                xanchor="center",
                x=0.5
            ),
                               margin=dict(t=50, b=100))
            st.plotly_chart(fig2, use_container_width=True)
