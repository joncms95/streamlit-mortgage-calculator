import streamlit as st
import math
import pandas as pd
import plotly.express as px


class MortgageCalculator:
    """A Streamlit app for various mortgage-related calculations."""

    CALCULATORS = [
        "Monthly Mortgage Estimation",
        "Home Affordability Estimation",
        "Upfront Costs Estimation",
    ]

    def __init__(self):
        st.session_state.setdefault("auto_check", True)
        st.session_state.setdefault("check_results", False)
        self.render()

    def render(self):
        # Reset check results
        st.session_state.check_results = False

        # Sidebar
        self.render_sidebar()

        # Main
        st.title("Mortgage Calculator :house:")
        st.caption(
            "Disclaimer: This tool is designed for mortgage calculations in Malaysia and provides estimation only"
        )

        if self.page == "Monthly Mortgage Estimation":
            return self.show_monthly_mortgage()
        if self.page == "Home Affordability Estimation":
            return self.show_home_affordability()
        if self.page == "Upfront Costs Estimation":
            return self.show_upfront_costs()

    def render_sidebar(self):
        with st.sidebar:
            st.title("Calculators :1234:")
            self.page = st.selectbox(
                "*Select an option: :point_down:", self.CALCULATORS
            )
            self.auto_check = st.toggle(
                "Always Check Results", value=st.session_state.auto_check
            )

            st.divider()

            if not self.auto_check:
                self.check_button()

    def check_button(self):
        if st.button("Check Results"):
            st.session_state.check_results = True

    def show_monthly_mortgage(self):
        st.header(f"{self.page}", divider=True)
        st.subheader(f"Data Input", divider=True)

        property_price = st.number_input(
            "Property Price ($)", min_value=50000, value=300000, step=100000
        )
        loan_amount = st.number_input(
            "Loan Amount ($)",
            min_value=90000,
            value=int(property_price * 0.9),
            step=100000,
            help="Loan amount will be automatically calculated as 90% of property price unless stated otherwise",
        )
        interest_rate = st.number_input(
            "Interest Rate (%)", min_value=0.01, value=3.9, step=0.05
        )
        loan_tenure = st.selectbox(
            "Loan Tenure (Years)",
            list(range(5, 36)),
            index=30,
        )

        # Check for maintenance fees
        has_maintenance_fees = st.toggle("Include maintenance fees? :wrench:")
        if has_maintenance_fees:
            square_feet = st.number_input(
                "Unit Size (sq ft)",
                min_value=100,
                value=900,
                step=100,
            )
            st.caption(f"Price per sq ft ($): {round(property_price / square_feet, 2)}")
            maintenance_fees_per_sqft = st.number_input(
                "Maintenance Fees per sq ft ($)",
                min_value=0.0,
                value=0.3,
                step=0.05,
            )

        # Show results
        if self.auto_check or st.session_state.check_results:
            monthly_payment = self.calculate_monthly_payment(
                loan_amount, interest_rate, loan_tenure
            )

            results = {
                "Monthly Instalment": f"${monthly_payment:,.2f}",
            }

            if has_maintenance_fees:
                maintenance_cost = square_feet * maintenance_fees_per_sqft
                total_monthly_payment = monthly_payment + maintenance_cost

                results.update(
                    {
                        "Maintenance Fees": f"${maintenance_cost:,.2f}",
                        ":red[Total Monthly Payment]": f"${total_monthly_payment:,.2f}",
                    }
                )

            self.display_results(results)

            st.markdown("***")

            # Plot chart
            schedule = []
            monthly_interest_rate = (interest_rate / 100) / 12
            remaining_balance = loan_amount

            for month in range(1, loan_tenure * 12 + 1):
                interest_payment = remaining_balance * monthly_interest_rate
                principal_payment = monthly_payment - interest_payment
                remaining_balance -= principal_payment

                schedule.append(
                    {
                        "Month": month,
                        "Principal Payment": round(principal_payment, 2),
                        "Interest Payment": round(interest_payment, 2),
                        "Total Payment": round(monthly_payment, 2),
                        "Remaining Balance": round(remaining_balance, 2),
                    }
                )

                if remaining_balance <= 0:
                    break

            df_schedule = pd.DataFrame(schedule)

            # Principal vs. Interest Payments
            fig_principal_interest = px.line(
                df_schedule,
                x="Month",
                y=["Principal Payment", "Interest Payment"],
                title="Principal and Interest Payments Over Time",
                labels={"value": "Amount ($)", "Month": "Month"},
                markers=True,
                color_discrete_map={
                    "Principal Payment": "green",
                    "Interest Payment": "red",
                },
            )
            fig_principal_interest.update_layout(
                xaxis_title="Month",
                yaxis_title="Amount ($)",
                xaxis=dict(showline=True, showgrid=False),
                yaxis=dict(showline=True, showgrid=True),
                legend_title="Payment Type",
            )

            # Remaining Balance
            fig_remaining_balance = px.line(
                df_schedule,
                x="Month",
                y="Remaining Balance",
                title="Remaining Balance Over Time",
                labels={"Remaining Balance": "Remaining Balance ($)", "Month": "Month"},
                markers=True,
            )
            fig_remaining_balance.update_layout(
                xaxis_title="Month",
                yaxis_title="Remaining Balance ($)",
                xaxis=dict(showline=True, showgrid=False),
                yaxis=dict(showline=True, showgrid=True),
            )

            tab1, tab2 = st.tabs(
                ["📈 Principal vs. Interest Payments", "📉 Remaining Balance"]
            )
            with tab1:
                st.plotly_chart(fig_principal_interest)
            with tab2:
                st.plotly_chart(fig_remaining_balance)

            # Amoritsation Schedule
            st.markdown("#### Amoritsation Schedule")
            st.dataframe(
                df_schedule,
                use_container_width=True,
                on_select="rerun",
                selection_mode=["multi-column"],
            )

            csv = df_schedule.to_csv(index=False)
            st.download_button(
                label="Download Schedule as CSV", data=csv, mime="text/csv"
            )

    def show_home_affordability(self):
        st.header(f"{self.page}", divider=True)
        st.subheader(f"Data Input", divider=True)

        monthly_income = st.number_input(
            "Monthly Net Income ($)",
            min_value=3000,
            value=5000,
            step=1000,
            help="Monthly net income refers to the income you receive after tax, EPF and other required salary deductions",
        )
        monthly_debts = st.number_input(
            "Monthly Commitments ($)",
            min_value=0,
            value=500,
            step=100,
            help="Monthly commitments refers to any monthly payments to banks, such as payments for car loans, non-banking companies, such as instalments for electronic purchases",
        )
        interest_rate = st.number_input(
            "Interest Rate (%)", min_value=0.01, value=3.9, step=0.05
        )
        loan_tenure = st.selectbox(
            "Loan Tenure (Years)",
            list(range(5, 36)),
            index=30,
        )

        # Show results
        if self.auto_check or st.session_state.check_results:
            max_property_price = self.calculate_home_affordability(
                monthly_income, monthly_debts, interest_rate, loan_tenure
            )

            # Check if monthly debts are too high
            if max_property_price == 0:
                warning_msg = "⚠️ Your monthly commitments exceed 40% of your monthly income. Please reduce your monthly commitments to afford a home."
                st.warning(warning_msg)
                self.display_results({"Suggested Property Value": "$0.00"})
            else:
                self.display_results(
                    {"Suggested Property Value": f"${max_property_price:,.2f}"}
                )

            st.markdown("***")

            # Plot chart
            min_income = max(3000, int(monthly_income * 0.5))
            max_income = max(int(monthly_income * 2.0), monthly_income + 5000)
            min_income = (min_income // 1000) * 1000
            max_income = ((max_income // 1000) + 1) * 1000

            # Determine step size based on range
            income_range = max_income - min_income
            if income_range <= 10000:
                step = 1000
            elif income_range <= 20000:
                step = 2000
            else:
                step = 5000

            incomes = list(range(min_income, max_income + step, step))
            user_income = int(monthly_income)
            if user_income not in incomes and min_income <= user_income <= max_income:
                incomes.append(user_income)
                incomes.sort()

            affordabilities = [
                self.calculate_home_affordability(
                    income, monthly_debts, interest_rate, loan_tenure
                )
                for income in incomes
            ]

            # Filter out negative values and ensure non-negative for chart
            chart_data = [
                (inc, aff) for inc, aff in zip(incomes, affordabilities) if aff > 0
            ]
            if chart_data:
                chart_incomes, chart_affordabilities = zip(*chart_data)
                chart_incomes = list(chart_incomes)
                chart_affordabilities = list(chart_affordabilities)

                # Create color array to highlight user's current income
                colors = []
                user_income_in_chart = False
                for inc in chart_incomes:
                    # Check if this income matches user's actual income
                    if inc == user_income:
                        colors.append("rgba(255, 0, 0, 0.8)")  # Red for user's income
                        user_income_in_chart = True
                    else:
                        colors.append("rgba(31, 119, 180, 0.8)")  # Blue for others

                fig = px.bar(
                    x=list(chart_incomes),
                    y=list(chart_affordabilities),
                    labels={"x": "Monthly Income ($)", "y": "Maximum Home Price ($)"},
                )

                # Apply custom colors
                fig.update_traces(
                    marker_color=colors,
                    texttemplate="%{y:$,.0f}",  # Format text labels to show dollar amounts
                    textposition="outside",  # Position text outside the bars
                )
                fig.update_layout(
                    title="Home Affordability vs. Monthly Income",
                    xaxis=dict(tickformat="$,.0f"),
                    yaxis=dict(tickformat="$,.0f"),
                )
                st.plotly_chart(fig)
                if user_income_in_chart:
                    st.caption("🔴 Red bar indicates your current monthly income")
            else:
                st.info(
                    "📊 Chart not available: Monthly commitments are too high for the income range shown. "
                    "Reduce your monthly commitments to see affordability projections."
                )
            st.caption(
                """
                **Calculations are done assuming a debt-to-income ratio of 40%**
                """
            )

    def show_upfront_costs(self):
        st.header(f"{self.page}", divider=True)
        st.subheader(f"Data Input", divider=True)

        property_price = st.number_input(
            "Property Price ($)", min_value=50000, value=300000, step=100000
        )
        loan_amount = st.number_input(
            "Loan Amount ($)",
            min_value=90000,
            value=int(property_price * 0.9),
            step=100000,
            help="Loan amount will be automatically calculated as 90% of property price unless stated otherwise",
        )
        discount_percent = st.number_input(
            "Discount (%)",
            min_value=0,
            max_value=100,
            value=0,
            step=1,
            help="Percentrage discount given by seller on the property price",
        )
        down_payment_percent = st.number_input(
            "Down Payment (%)",
            value=int(10 - discount_percent),
            disabled=True,
            help="Down payment starts at 10% and decreases based on the discount given",
        )
        stamp_duty_percent = st.number_input(
            "Stamp Duty for Loan Agreement (%)",
            min_value=0.1,
            value=0.5,
            step=0.05,
            disabled=True,
            help="Stamp duty for loan agreement is calculated as 0.5% of loan amount",
        )

        # Check waived fees
        has_waived_fees = st.toggle("Any waived fees? :grinning:")
        waived_fees = {
            "loan_stamp_duty": (
                st.checkbox("Stamp Duty for Loan Agreement (LA)")
                if has_waived_fees
                else False
            ),
            "mot_stamp_duty": (
                st.checkbox("Stamp Duty for Memorandum of Transfer (MOT)")
                if has_waived_fees
                else False
            ),
            "loan_legal_fees": (
                st.checkbox("Legal Fees for Loan Agreement")
                if has_waived_fees
                else False
            ),
            "spa_legal_fees": (
                st.checkbox("Legal Fees for Sales & Purchase Agreement (SPA)")
                if has_waived_fees
                else False
            ),
        }

        # Show results
        if self.auto_check or st.session_state.check_results:
            down_payment = self.calculate_down_payment(
                property_price, down_payment_percent
            )
            loan_stamp_duty = (
                0
                if waived_fees["loan_stamp_duty"]
                else self.calculate_loan_stamp_duty(loan_amount, stamp_duty_percent)
            )
            mot_stamp_duty = (
                0
                if waived_fees["mot_stamp_duty"]
                else self.calculate_mot_stamp_duty(property_price)
            )
            loan_legal_fees = (
                0
                if waived_fees["loan_legal_fees"]
                else self.calculate_legal_fees(property_price)
            )
            spa_legal_fees = (
                0
                if waived_fees["spa_legal_fees"]
                else self.calculate_legal_fees(property_price)
            )
            total_fees = (
                loan_stamp_duty + mot_stamp_duty + loan_legal_fees + spa_legal_fees
            )
            total_upfront_costs = down_payment + total_fees

            total_label = ":red[Total Upfront Costs] (:heavy_minus_sign:)"
            pie_labels = [
                "Stamp Duty for LA",
                "Stamp Duty for MOT",
                "Legal Fees for LA",
                "Legal Fees for SPA",
            ]
            pie_values = [
                loan_stamp_duty,
                mot_stamp_duty,
                loan_legal_fees,
                spa_legal_fees,
            ]

            if discount_percent > 10:
                down_payment_label = ":green[Rebates] (:heavy_plus_sign:)"
                if abs(down_payment) > (total_fees):
                    total_label = ":green[Total Rebates] (:heavy_plus_sign:)"
            else:
                down_payment_label = ":red[Down Payment] (:heavy_minus_sign:)"
                pie_labels.append("Down Payment")
                pie_values.append(down_payment)

            results = {
                down_payment_label: f"${abs(down_payment):,.2f}",
                "Stamp Duty for LA": f"${loan_stamp_duty:,.2f}",
                "Stamp Duty for MOT": f"${mot_stamp_duty:,.2f}",
                "Legal Fees for LA": f"${loan_legal_fees:,.2f}",
                "Legal Fees for SPA": f"${spa_legal_fees:,.2f}",
                total_label: f"${abs(total_upfront_costs):,.2f}",
            }

            self.display_results(results)

            st.markdown("***")

            # Plot chart
            if any(pie_values):
                fig = px.pie(
                    names=pie_labels,
                    values=pie_values,
                    hole=0.4,
                    labels={"names": "Category", "values": "Amount ($)"},
                )
                fig.update_traces(
                    textposition="outside", textinfo="percent+label+value"
                )
                fig.update_layout(title="Upfront Costs Distribution")
                st.plotly_chart(fig)

            with st.sidebar:
                st.caption(
                    """
                    **MOT Stamp Duty Calculation:**
                    - **Up to RM100,000:** 1% of the property price.
                    - **RM100,001 to RM500,000:** RM1,000 + 2% of the amount above RM100,000.
                    - **RM500,001 to RM1,000,000:** RM9,000 + 3% of the amount above RM500,000.
                    - **Above RM1,000,000:** RM24,000 + 4% of the amount above RM1,000,000.

                    **Legal Fees Calculation:**
                    - **Up to RM500,000:** 1.25% of property price, with minimum of RM500
                    - **RM500,000 to RM7,000,000:** RM6,250 + 1% of the amount above RM500,000
                    - **Above RM7,000,000:** RM76,250
                    """
                )

    # Utility Methods for Calculations
    def calculate_monthly_payment(self, loan_amount, interest_rate, loan_tenure):
        monthly_rate = interest_rate / 100 / 12
        num_payments = loan_tenure * 12

        if interest_rate == 0:
            return loan_amount / num_payments

        return (
            loan_amount
            * (monthly_rate * math.pow(1 + monthly_rate, num_payments))
            / (math.pow(1 + monthly_rate, num_payments) - 1)
        )

    def calculate_home_affordability(
        self, monthly_income, monthly_debts, interest_rate, loan_tenure
    ):
        # Assuming a debt-to-income ratio of 40%
        max_monthly_payment = (monthly_income * 0.40) - monthly_debts

        # If monthly debts exceed the total debt ratio, no affordable property
        if max_monthly_payment <= 0:
            return 0

        max_loan = (
            max_monthly_payment
            * (math.pow(1 + interest_rate / 100 / 12, loan_tenure * 12) - 1)
            / (
                interest_rate
                / 100
                / 12
                * math.pow(1 + interest_rate / 100 / 12, loan_tenure * 12)
            )
        )

        return max_loan

    def calculate_down_payment(self, property_price, down_payment_percent):
        return property_price * down_payment_percent / 100

    def calculate_loan_stamp_duty(self, loan_amount, stamp_duty_percent):
        return loan_amount * stamp_duty_percent / 100

    def calculate_mot_stamp_duty(self, property_price):
        if property_price <= 100000:
            return 0.01 * property_price
        elif property_price <= 500000:
            return 1000 + (0.02 * (property_price - 100000))
        elif property_price <= 1000000:
            return 9000 + (0.03 * (property_price - 500000))
        else:
            return 24000 + (0.04 * (property_price - 1000000))

    def calculate_legal_fees(self, property_price):
        if property_price <= 500000:
            return max(property_price * 0.0125, 500)
        elif property_price > 7000000:
            return 76250
        elif property_price > 500000:
            return 6250 + (property_price - 500000) * 0.01

    def display_results(self, results):
        with st.sidebar:
            st.header("Results", divider=True)

            for key, value in results.items():
                col1, col2 = st.columns([2, 1])
                with col1:
                    st.markdown(f"**{key}**")
                with col2:
                    st.markdown(f"{value}")
            st.markdown("---")


if __name__ == "__main__":
    st.set_page_config("MY Mortgage Calculator", page_icon=":house:")
    MortgageCalculator()
