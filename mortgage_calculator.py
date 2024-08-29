import streamlit as st
import math
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
            "Disclaimer: This tool is designed for mortgage calculations in Malaysia and provides estimation only."
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

        loan_amount = st.number_input(
            "Loan Amount ($)", min_value=10000, value=300000, step=100000
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
                "Unit Size (sq ft)", min_value=100, value=900, step=100
            )
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
                "Monthly Installment": f"${monthly_payment:,.2f}",
            }

            if has_maintenance_fees:
                maintenance_cost = square_feet * maintenance_fees_per_sqft
                total_monthly_payment = monthly_payment + maintenance_cost

                results.update(
                    {
                        "Maintenance Fees": f"${maintenance_cost:,.2f}",
                        "Total Monthly Payment": f"${total_monthly_payment:,.2f}",
                    }
                )

            st.markdown("***")

            # Plot chart
            monthly_interest_rate = interest_rate / 100 / 12
            interest_payment = loan_amount * monthly_interest_rate
            principal_payment = monthly_payment - interest_payment

            fig = px.bar(
                x=["Principal Paid", "Interest Paid"],
                y=[principal_payment, interest_payment],
                labels={"x": "Payment Type", "y": "Amount ($)"},
                title="Principal and Interest Breakdown for the First Month",
                color=["Principal Paid", "Interest Paid"],
                color_discrete_map={"Principal Paid": "blue", "Interest Paid": "red"},
            )

            fig.update_layout(
                legend_title_text="Payment Breakdown", yaxis=dict(title="Amount ($)")
            )

            st.plotly_chart(fig)

            self.display_results(results)

    def show_home_affordability(self):
        st.header(f"{self.page}", divider=True)
        st.subheader(f"Data Input", divider=True)

        monthly_income = st.number_input(
            "Monthly Net Income ($)", min_value=3000, value=5000, step=1000
        )
        monthly_debts = st.number_input(
            "Monthly Commitments ($)", min_value=0, value=500, step=100
        )
        interest_rate = st.number_input(
            "Interest Rate (%)", min_value=0.01, value=3.9, step=0.01
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

            st.markdown("***")

            # Plot chart
            incomes = list(
                range(3000, 15001, 1000)
            )  # Monthly incomes from 3k to MYR 15k
            affordabilities = [
                self.calculate_home_affordability(
                    income, monthly_debts, interest_rate, loan_tenure
                )
                for income in incomes
            ]

            fig = px.bar(
                x=incomes,
                y=affordabilities,
                labels={"x": "Monthly Income ($)", "y": "Maximum Home Price ($)"},
            )
            fig.update_layout(title="Home Affordability vs. Monthly Income")

            st.plotly_chart(fig)

            self.display_results(
                {"Suggested Property Value": f"${max_property_price:,.2f}"}
            )

            st.caption(
                """
                **Calculations are done assuming a debt-to-income ratio of 30%**
                """
            )

    def show_upfront_costs(self):
        st.header(f"{self.page}", divider=True)
        st.subheader(f"Data Input", divider=True)

        property_price = st.number_input(
            "Property Price ($)", min_value=50000, value=300000, step=100000
        )
        loan_amount = st.number_input(
            "Loan Amount ($)", min_value=0, value=int(property_price * 0.9), step=100000
        )
        discount_percent = st.number_input(
            "Discount (%)", min_value=0, max_value=100, value=0, step=1
        )
        down_payment_percent = st.number_input(
            "Down Payment (%)", value=int(10 - discount_percent), disabled=True
        )
        stamp_duty_percent = st.number_input(
            "Stamp Duty for Loan Agreement (%)",
            min_value=0.1,
            value=0.5,
            step=0.05,
            disabled=True,
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
            "legal_fees": st.checkbox("Legal Fees") if has_waived_fees else False,
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
            legal_fees = (
                0
                if waived_fees["legal_fees"]
                else self.calculate_legal_fees(property_price)
            )
            total_upfront_costs = down_payment + loan_stamp_duty + mot_stamp_duty

            if discount_percent > 10:
                down_payment_label = "Rebates"
                if abs(down_payment) > loan_stamp_duty + mot_stamp_duty:
                    total_label = "Total Rebates"
                else:
                    total_label = "Total Upfront Costs"
                pie_labels = ["Stamp Duty for LA", "Stamp Duty for MOT", "Legal Fees"]
                pie_values = [loan_stamp_duty, mot_stamp_duty, legal_fees]
            else:
                down_payment_label = "Down Payment"
                total_label = "Total Upfront Costs"
                pie_labels = [
                    "Down Payment",
                    "Stamp Duty for LA",
                    "Stamp Duty for MOT",
                    "Legal Fees",
                ]
                pie_values = [down_payment, loan_stamp_duty, mot_stamp_duty, legal_fees]

            st.markdown("***")

            # Plot chart
            fig = px.pie(
                names=pie_labels,
                values=pie_values,
                hole=0.4,
                labels={"names": "Category", "values": "Amount ($)"},
            )
            fig.update_layout(title="Upfront Costs Distribution")

            st.plotly_chart(fig)

            results = {
                down_payment_label: f"${abs(down_payment):,.2f}",
                "Stamp Duty for LA": f"${loan_stamp_duty:,.2f}",
                "Stamp Duty for MOT": f"${mot_stamp_duty:,.2f}",
                "Legal Fees": f"${legal_fees:,.2f}",
                total_label: f"${abs(total_upfront_costs):,.2f}",
            }

            self.display_results(results)

            st.caption(
                """
                **For properties up to RM100,000:**
                - MOT is calculated as **1%** of the property price.

                **For properties between RM100,001 and RM500,000:**
                - MOT is calculated as **RM1,000** + **2%** of the amount above RM100,000.

                **For properties above RM500,000:**
                - MOT is calculated as **RM1,000** + **RM8,000** + **3%** of the amount above RM500,000.
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
        # Assuming a debt-to-income ratio of 30%
        max_monthly_payment = (monthly_income * 0.30) - monthly_debts
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
            return 1000 + 0.02 * (property_price - 100000)
        else:
            return 1000 + 8000 + 0.03 * (property_price - 500000)

    def calculate_legal_fees(self, property_price):
        if property_price <= 500000:
            fee = property_price * 0.01
        elif property_price <= 1000000:
            fee = 5000 + (property_price - 500000) * 0.008
        elif property_price <= 3000000:
            fee = 9000 + (property_price - 1000000) * 0.007
        elif property_price <= 5000000:
            fee = 24000 + (property_price - 3000000) * 0.006
        else:
            fee = 36000 + (property_price - 5000000) * 0.005

        return fee

    def display_results(self, results):
        with st.sidebar:
            st.subheader("Results", divider=True)

            for key, value in results.items():
                col1, col2 = st.columns([2, 1])
                with col1:
                    st.markdown(f"**{key}:**")
                with col2:
                    st.markdown(f"{value}")
            st.markdown("---")


if __name__ == "__main__":
    st.set_page_config("Mortgage Calculator", page_icon=":house:")
    MortgageCalculator()
